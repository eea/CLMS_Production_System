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
    'email': ['elena.jung@gaf.de'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'queue': 'reprocessing_test_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    #'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(hours=2),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

def failure(context):
    failed_dag(context['dag_run'].run_id)


def success(**context):
    success_dag(context['dag_run'].run_id)


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


def filenames_from_dict(files_dict, features):
    print(f"files_dict {files_dict}")
    files_as_list = []
    for feat in features:
        feat = feat.strip()
        if not feat:
            continue
        if feature_is_pre_calculated(feat):
            filepath = files_dict[feat]
            files_as_list.append(filepath)
            print(f"filepath: {filepath}")
            continue
        if feat.count("_") == 2:
            feat_parts = feat.split("_")
            band = feat_parts[0].strip()
            intrpl = feat_parts[1].strip()
            metric = feat_parts[2].strip()
            key = intrpl + "+" + metric
            filepath = files_dict[band][key]
            files_as_list.append(filepath)
            print(f"filepath: {filepath}")
            continue
        feat_parts = feat.split("_")
        band = feat_parts[0].strip()
        metric = feat_parts[1].strip()
        print(f"band {band}")
        print(f"metric {metric}")
        filepath = files_dict[band][metric]
        files_as_list.append(filepath)
        print(f"filepath: {filepath}")
    print("all files appended to list")
    print(f"files_as_list {files_as_list}")
    return files_as_list


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


def call_postprocessing_1(**kwargs): 
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    res = requests.get("http://postprocessing-testing-t1.task-1-testing:80/cell_for_reprocessing", params={"code": pu, 
    "process_id": pid})
    print(f"process id: {pid} - {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_reprocessing_{kwargs['task_instance'].task_id}")

    res.raise_for_status()
    kwargs['ti'].xcom_push(key='coordinates', value=res.json()['bounding_box'])


def call_calc_feature(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")
    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)
    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)
    data_filter = get_data_from_payload("data_filter", dict, True, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)

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
                value_dict["values"].append(value)
            else:
                value_dict["values"] = [value]
            feat_dict[key] = value_dict
        else:
            feat_dict[key] = {"values":[value]}
    data = {"features": feat_dict}
    print(f"features dictionary: {data}")

    if not feat_dict:
        kwargs['ti'].xcom_push(key='pre_calc_feats', value=pre_calc_feats)
        return "calcfeat_pre_calculated_features"

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='postprocessing_1')

    data["aoi"] = coordinates
    if data_filter:
        data["data_filter"] = data_filter # json.loads(data_filter) 
    data = json.dumps(data)

    path_prefix = "elena_test"

    params = {"process_id": pid, "data_source": "wekeo_S2", "resolution": "10", "cloudmask_type": "Fmask4", 
              "path_prefix": path_prefix, "start_date": start_date, "end_date": end_date, "max_cloudcover": cloud_cover, "epsg": "3035", 
              "aoi_coverage": aoi_coverage, "to_upload": True, "use_cache": use_cache, "resampling": "bi_cubic"}

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-testing-t1.task-1-testing:80/temporals2features', 
    params = params, data = data, headers = headers)
    print(f"process id: {pid} - {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_reprocessing_{kwargs['task_instance'].task_id}")

    res.raise_for_status()
    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return "set_invalid"
    kwargs['ti'].xcom_push(key='files', value=res.json())
    kwargs['ti'].xcom_push(key='calc_feat_params', value=params)
    data = json.loads(data)
    data["features"] = features
    data = json.dumps(data)
    kwargs['ti'].xcom_push(key='calc_feat_data', value=data)
    kwargs['ti'].xcom_push(key='pre_calc_feats', value=pre_calc_feats)
    return "calcfeat_pre_calculated_features"


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


def call_calc_feature_pre(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    ti = kwargs['ti']
    precalculated_features = ti.xcom_pull(key='pre_calc_feats', task_ids='calcfeat')
    print(f"precalculated_features: {precalculated_features}")
    if not precalculated_features:
        return "gafseg"

    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)

    path_prefix = "cfs/" + pu

    params = {"process_id": pid, "resolution": "10", "path_prefix": path_prefix, "epsg": "3035", "to_upload": True}

    coordinates = ti.xcom_pull(key='coordinates', task_ids='postprocessing_1')

    data = {"aoi": coordinates, "features": precalculated_features}
    data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-testing-t1.task-1-testing:80/pre_calculated_features', 
                        params = params, data = data, headers = headers)
    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_reprocessing_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return "set_invalid"

    files = res.json()["results"][0]["data"]
    print(f"files: {files}")
    ti.xcom_push(key="pre_calc_files", value=files)
    return "gafseg"


def call_gaf_seg(**kwargs): 
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    ti = kwargs['ti']

    results_from_calc_feature = ti.xcom_pull(key='files', task_ids='calcfeat') or {}
    try:
        calc_feat_data = results_from_calc_feature["results"][0]["data"]
    except KeyError:
        calc_feat_data = {}

    print(f"data from calc feat: {calc_feat_data}")
    files_pre_calc_feature = ti.xcom_pull(key='pre_calc_files', task_ids='calcfeat_pre_calculated_features')
    print(f"data from pre calc feat: {files_pre_calc_feature}")
    if files_pre_calc_feature:
        calc_feat_data.update(files_pre_calc_feature)
    features = get_data_from_payload("features", list, False, **kwargs)
    files = filenames_from_dict(calc_feat_data, features)

    rule_set = get_data_from_payload("rule_set", dict, False, **kwargs)
    #try:
    #    rule_set = json.loads(rule_set)
    #except Exception as e:
    #    raise(f"rule set was not able to be loaded as json: {e}")
    data = {"rulesetDict": rule_set}

    data["image_paths"] = files

    path_prefix = "christian_test"
    params = {"epsg": 3035, "path_prefix": path_prefix, "process_id": pid, "use_aoi": False}

    headers = {'Content-Type': 'application/json'}
    res = requests.post("http://gaf-seg-testing-t1.task-1-testing:80/segmentation", params = params, json = data, headers = headers)
    print(f"process id: {pid} - {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_reprocessing_{kwargs['task_instance'].task_id}")

    res.raise_for_status()
    kwargs['ti'].xcom_push(key='segmented_file', value=res.json())
    kwargs['ti'].xcom_push(key='gaf_seg_params', value=params)
    kwargs['ti'].xcom_push(key='gaf_seg_data', value=data)


def call_postprocessing_2(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}"

    ti = kwargs['ti']
    result_from_gafseg = ti.xcom_pull(key='segmented_file', task_ids='gafseg')
    segmented_file = result_from_gafseg["result"]

    params = {"s3_key": segmented_file, "process_id": pid}

    calc_feat_params = ti.xcom_pull(key='calc_feat_params', task_ids='calcfeat') or {}
    calc_feat_data = ti.xcom_pull(key='calc_feat_data', task_ids='calcfeat') or {}
    gaf_seg_params = ti.xcom_pull(key='gaf_seg_params', task_ids='gafseg')
    gaf_seg_data = ti.xcom_pull(key='gaf_seg_data', task_ids='gafseg')
    data = {"calc_feat_data": json.loads(calc_feat_data),
            "calc_feat_params": calc_feat_params,
            "gaf_seg_data": gaf_seg_data,
            "gaf_seg_params": gaf_seg_params}
    data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://postprocessing-testing-t1.task-1-testing:80/softbone', 
    params = params, headers = headers, data=data)
    print(f"process id: {pid} - {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_reprocessing_{kwargs['task_instance'].task_id}")

    res.raise_for_status()


dag = DAG(
    "task1_reprocessing_test",
    default_args=default_args,
    description='task1 reprocessing TEST',
    schedule_interval=None,
    on_failure_callback=failure,
    #on_success_callback=success,
    max_active_runs=8,
    concurrency=8,
)

dag.doc_md = """
#### DAG Summary
Pipeline to calculate features and apply model.
"""

status = PythonOperator(task_id=f"status",
    provide_context=True,
    python_callable=state_function,
    dag=dag)

postprocessing_1 = PythonOperator(task_id=f"postprocessing_1",
    provide_context=True,
    python_callable=call_postprocessing_1,
    dag=dag)

calcfeat = BranchPythonOperator(task_id=f"calcfeat",
    provide_context=True,
    python_callable=call_calc_feature,
    dag=dag)

calcfeat_pre = BranchPythonOperator(task_id="calcfeat_pre_calculated_features",
    provide_context=True,
    python_callable=call_calc_feature_pre,
    trigger_rule="none_failed",
    dag=dag)

gafseg = PythonOperator(task_id=f"gafseg",
    provide_context=True,
    python_callable=call_gaf_seg,
    dag=dag)

postprocessing_2 = PythonOperator(task_id=f"postprocessing_2",
    provide_context=True,
    python_callable=call_postprocessing_2,
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


#status >> postprocessing_1 >> calcfeat >> gafseg >> postprocessing_2
status >> postprocessing_1 >> calcfeat >> set_invalid
calcfeat >> calcfeat_pre >> set_invalid
calcfeat_pre >> gafseg >> postprocessing_2 >> finished
