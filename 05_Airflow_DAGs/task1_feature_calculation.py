from datetime import timedelta
import airflow
import os
import json
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow import DAG
import requests
import shutil
import copy
from geoville_ms_dag_state.dag_state import * 
from airflow.operators.dummy_operator import DummyOperator
from geoville_ms_logging.geoville_ms_logging import *


# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(7),
    'email': ['sooyeon.chun@gaf.de'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
    'queue': 'task1_feature_calculation',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(hours=2.5),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

def failure(context):
    failed_dag(context['dag_run'].run_id)


def success(**context):
    success_dag(context['dag_run'].run_id, "success")


def set_invalid(**context):
    invalid_dag(context['dag_run'].run_id, 'No Data found')


def state_function(**context):
    running_dag(context['run_id'])


#def failure(context):
#    print('failure')


#def success(context):
#    print('success')


def feature_is_pre_calculated(feat):
    exact_matches = ["X", "Y", "CopernicusDSM", "EUDEM", "GEnSPCA"]
    prefix_matches = ["CopernicusDSM", "DistCoarse", "DLT", "Geomorpho90m", "ProbaFilt", "WAW"]

    return feat in exact_matches or any(feat.startswith(prefix) for prefix in prefix_matches)

    
def get_data_from_payload(param_name: str, data_type, use_default_value: bool, **kwargs):
    try:
        data = kwargs['dag_run'].conf[param_name]
        print(f"{param_name} from api: {data}")
    except KeyError:
        if use_default_value:
            data = 0 if data_type == int else None
        else:
            raise KeyError(f"The following parameter cannot be found in the payload object: {param_name}")
    except Exception as e:
        raise Exception(f"something went wrong with retrieving the {param_name}: {e}")
    
    if not use_default_value and not isinstance(data, data_type):
        raise TypeError(f"{param_name} is not of type {data_type}")

    return data


def call_grid_service(**kwargs): 
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    res = requests.get("http://grid-prod.task-1-production:5000/eea_grid", params={"cell_code_input": pu, 
    "process_id": pid})
    print(f"process id: {pid} - {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_featurecalculation_{kwargs['task_instance'].task_id}")
    res.raise_for_status()
    kwargs['ti'].xcom_push(key='coordinates', value=res.json()["aoi"])
    kwargs['ti'].xcom_push(key='epsg', value=res.json()["epsg"])
    print(f"epsg returned from grid service: {res.json()['epsg']}")


def call_calc_feature(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc"
    print(f"process id {pid}")

    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    features = get_data_from_payload("features", list, False, **kwargs)

    pre_calc_feats = []
    feat_dict = {}
    for feat in features:
        feat = feat.strip()
        if not feat:
            continue
        if feature_is_pre_calculated(feat):
            pre_calc_feats.append(feat)
            continue
        if feat.count("_") > 2 or feat.count("_") == 0:
            raise Exception(f"{feat} is not in the correct format - not the right amount of underscores")
        if feat.count("_") == 2:
            add_intrpl_to_feat_dict(feat, feat_dict, start_date, end_date)
            continue
        feat_parts = feat.split("_")
        key = feat_parts[0].strip()
        value = feat_parts[1].strip()
        if key in feat_dict:
            value_dict = feat_dict[key]
            if "values" in value_dict:
                if value in value_dict["values"]:
                    continue
                value_dict["values"].append(value)
            else:
                value_dict["values"] = [value]
            feat_dict[key] = value_dict
        else:
            feat_dict[key] = {"values":[value]}
    print(f"pre-calculated features {pre_calc_feats}")
    print(f"S2 features {feat_dict}")

    if feat_dict:
        is_data_valid = call_calc_feature_s2(feat_dict, pu, pid, **kwargs)
        if not is_data_valid:
            return "set_invalid"
    else:
        print("no s2 bands requested")

    if pre_calc_feats:
        is_data_valid = call_calc_feature_pre(pre_calc_feats, pu, pid, **kwargs)
        if not is_data_valid:
            return "set_invalid"
    else:
        print("no pre calculated features requested")

    return "finished"


def call_calc_feature_s2(feat_dict, pu, pid, **kwargs):
    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)
    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)
    data_filter = get_data_from_payload("data_filter", str, True, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)

    data = {"features": feat_dict}

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')

    data["aoi"] = coordinates
    cm_type = "Fmask4"
    if data_filter:
        data_filter_params = json.loads(data_filter)
        if "cm" in data_filter_params:
            print(data_filter_params["cm"])
            cm_type = data_filter_params.pop("cm")
            if cm_type == 'scl':
                cm_type ='SCL'
            if cm_type == 'scl_enhanced':
                cm_type = 'SCL_ENHANCED'
        data["data_filter"] = data_filter_params
    data = json.dumps(data)
    print(f"S2 data: {data}")

    path_prefix = "task1_cfs/" + pu
    print(f"path_prefix: {path_prefix}")
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    params = {"process_id": pid, "data_source": "wekeo_S2", "resolution": "10", "cloudmask_type": cm_type, 
              "path_prefix": path_prefix, "start_date": start_date, "end_date": end_date, "max_cloudcover": cloud_cover, "epsg": epsg, 
              "aoi_coverage": aoi_coverage, "to_upload": True, "use_cache": use_cache, "resampling": "bi_cubic"}
    print(f"S2 params: {params}")

    headers = {'Content-Type': 'application/json'}

    print(f"calling temporals 2 features")
    res = requests.post('http://cfs-doms-task-1-prod.task-1-production:5000/temporals2features', 
    params = params, data = data, headers = headers)
    
    print(f"finished calling temporals 2 features")
    if len(res.text) < 20000:
        print(f"S2 process id {pid}: {res.text}")
    else:
        print(f"S2 process id {pid}: {res.status_code}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_featurecalculation_{kwargs['task_instance'].task_id}")
    res.raise_for_status()
    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return False
    
    return True


def add_intrpl_to_feat_dict(feat, feat_dict, start_date, end_date):
    feat_parts = feat.split("_")
    key = feat_parts[0].strip()
    intrpl = feat_parts[1].strip()
    value = feat_parts[2].strip()
    print(f"key, intrpl, value {key, intrpl, value}")
    if key in feat_dict:
        if intrpl in feat_dict[key]:
            intrpl_dict = feat_dict[key][intrpl]
            intrpl_dict["features"].append(value)
            feat_dict[key][intrpl] = intrpl_dict
            print(f"intrpl_dict intrpl already exists {intrpl_dict}")
        else:
            intrpl_dict = {"end_date": end_date, "features": [value], "file_format": "tiff", "interval_size": 10, "start_date": start_date}
            feat_dict[key][intrpl] = intrpl_dict
            print(f"intrpl_dict intrpl does not exist yet {intrpl_dict}")
    else:
        intrpl_dict = {"end_date": end_date, "features": [value], "file_format": "tiff", "interval_size": 10, "start_date": start_date}
        feat_dict[key] = {intrpl: intrpl_dict}
        print(f"intrpl_dict key does not exist yet {intrpl_dict}")


def call_calc_feature_pre(pre_calc_feats, pu, pid, **kwargs):
    path_prefix = "task1_cfs/" + pu
    ti = kwargs['ti']
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')
    params = {"process_id": pid, "resolution": "10", "path_prefix": path_prefix, "epsg": epsg, "to_upload": True}
    print(f"full pre calc feature params: {params}")

    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')

    data = {"aoi": coordinates, "features": pre_calc_feats}
    data = json.dumps(data)
    print(f"full pre calc feature data: {data}")

    headers = {'Content-Type': 'application/json'}

    print(f"calling pre calculated features")
    res = requests.post('http://cfs-doms-task-1-prod.task-1-production:5000/pre_calculated_features', 
                        params = params, data = data, headers = headers)
    
    print(f"finished calling pre calculated features")
    if len(res.text) < 20000:
        print(f"pre calculated features process id {pid}: {res.text}")
    else:
        print(f"pre calculated features process id {pid}: {res.status_code}")

    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_batchclassification_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return False

    return True


dag = DAG(
    "task1_feature_calculation",
    default_args=default_args,
    description='task1 feature calculation DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    #on_success_callback=success,
    max_active_runs=15,
    concurrency=15,
)

dag.doc_md = """
#### DAG Summary
Pipeline to calculate features and apply model.
"""

status = PythonOperator(task_id=f"status",
    provide_context=True,
    python_callable=state_function,
    dag=dag)

grid = PythonOperator(task_id=f"grid",
    provide_context=True,
    python_callable=call_grid_service,
    dag=dag)

calcfeat = BranchPythonOperator(task_id=f"calcfeat",
    provide_context=True,
    python_callable=call_calc_feature,
    trigger_rule="none_failed",
    dag=dag)

set_invalid = PythonOperator(task_id="set_invalid",
    provide_context=True,
    python_callable=set_invalid,
    trigger_rule="none_failed",
    dag=dag)

finished = PythonOperator(task_id="finished", 
    provide_context=True,
    python_callable=success,
    trigger_rule="none_failed",
    dag=dag)


status >> grid >> calcfeat >> set_invalid
calcfeat >> finished
