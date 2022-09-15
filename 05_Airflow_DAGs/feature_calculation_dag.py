from datetime import timedelta
import airflow
import os
import json
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.exceptions import AirflowSkipException
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
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
    'queue': 'feature_calculation_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': True,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(hours=4),
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
    invalid_dag(context['dag_run'].run_id, "No Data found")


def state_function(**context):
    running_dag(context['run_id'])


#def failure(context):
#    print('failure')


#def success(context):
#    print('success')


def call_grid_service(**kwargs): 
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc" #
    print(f"process id {pid}")

    res = requests.get("http://grid-service-prod-t2.task-2-production:80/eea_grid", params={"cell_code_input": pu, "process_id": pid})
    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_featurecalculation_{kwargs['task_instance'].task_id}")
    res.raise_for_status()
    kwargs['ti'].xcom_push(key='coordinates', value=res.json()["aoi"])
    kwargs['ti'].xcom_push(key='epsg', value=res.json()["epsg"])


def call_calc_feature_s1(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc"
    print(f"process id {pid}")

    s1_bands = get_data_from_payload("s1_bands", list, True, **kwargs)
    if not (s1_bands and s1_bands[0]):
        return "calcfeat_temporals2features"

    if isinstance(s1_bands[0], list):
        s1_bands = s1_bands[0]

    bands_asc = []
    bands_dsc = []
    for band in s1_bands:
        direction_band = band.split("_")
        if direction_band[0].upper() == "ASC":
            bands_asc.append(direction_band[1])
        elif direction_band[0].upper() == "DSC":
            bands_dsc.append(direction_band[1])
        else:
            gemslog(LogLevel.ERROR, f"{band} not in the correct format", order_id=pid, service_name=f"task2_featurecalculation_{kwargs['task_instance'].task_id}")
            raise Exception(f"{band} not in the correct format. The correct format is 'DSC_band' or 'ASC_band'") 

    if bands_asc:
        data_found = send_request(bands_asc, "ascending", pid, **kwargs)
        if not data_found:
            return "set_invalid"

    if bands_dsc:
        data_found = send_request(bands_dsc, "descending", pid, **kwargs)
        if not data_found:
            return "set_invalid"

    
    return "calcfeat_temporals2features"

    
def call_calc_feature_s2(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc"
    print(f"process id {pid}")

    s2_bands = get_data_from_payload("s2_bands", list, True, **kwargs)
    if not (s2_bands and s2_bands[0]):
        return "calcfeat_pre_calculated_features"

    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    interval_size = get_data_from_payload("interval_size", int, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)

    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)

    data_filter_s2 = get_data_from_payload("data_filter_s2", str, True, **kwargs)

    path_prefix = "cfs/" + pu

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    params = {"process_id": pid, "data_source": "wekeo_S2", "resolution": "10", "cloudmask_type": "Fmask4", 
              "path_prefix": path_prefix, "start_date": start_date, "end_date": end_date, "max_cloudcover": cloud_cover, "epsg": epsg, 
              "aoi_coverage": aoi_coverage, "to_upload": True, "use_cache": use_cache}

    if kwargs['task_instance'].try_number > 3:
        params["use_cache"] = "False"
        print("use_cache has been set to false")
    print(f"full params: {params}")

    if isinstance(s2_bands[0], list):
        s2_bands = s2_bands[0]

    data = create_calc_feat_data(start_date, end_date, s2_bands, interval_size, coordinates, data_filter_s2, True)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals2features', 
                        params = params, data = data, headers = headers)

    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_featurecalculation_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return "set_invalid"

    print(f"files: {res.json()}")

    return "calcfeat_pre_calculated_features"


def call_calc_feature_pre(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc"
    print(f"process id {pid}")

    precalculated_features = get_data_from_payload("precalculated_features", list, True, **kwargs)
    if not (precalculated_features and precalculated_features[0]):
        s1_bands = get_data_from_payload("s1_bands", list, True, **kwargs)
        s2_bands = get_data_from_payload("s2_bands", list, True, **kwargs)
        if not (s1_bands and s1_bands[0]) and not (s2_bands and s2_bands[0]):
            return "calcfeat_dsl_only"  # only call fmask4 if S1, S2 and pre_calc are empty, otherwise call finished
        return "tasks_completed"

    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    interval_size = get_data_from_payload("interval_size", int, False, **kwargs)

    path_prefix = "cfs/" + pu

    ti = kwargs['ti']
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    params = {"process_id": pid, "resolution": "10", "path_prefix": path_prefix, "epsg": epsg, "to_upload": True}
    print(f"pre calculated features params: {params}")

    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')

    if isinstance(precalculated_features[0], list):
        precalculated_features = precalculated_features[0]

    data = {"aoi": coordinates, "features": precalculated_features}
    data = json.dumps(data)
    print(f"pre calculated features data: {data}")

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/pre_calculated_features', 
                        params = params, data = data, headers = headers)

    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_featurecalculation_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return "set_invalid"

    print(f"files: {res.json()}")

    return "tasks_completed"


def call_fmask4(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_featcalc"
    print(f"process id {pid}")

    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)

    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)

    data_filter_s2 = get_data_from_payload("data_filter_s2", str, True, **kwargs)

    path_prefix = "cfs/" + pu

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    params = {"process_id": pid, "data_source": "wekeo_S2", "resolution": "10", "cloudmask_type": "Fmask4", 
              "path_prefix": path_prefix, "start_date": start_date, "end_date": end_date, "max_cloudcover": cloud_cover, "epsg": epsg, 
              "aoi_coverage": aoi_coverage, "to_upload": True, "use_cache": use_cache}

    if kwargs['task_instance'].try_number > 3:
        params["use_cache"] = "False"
        print("use_cache has been set to false")
    print(f"full params: {params}")

    data = create_data_fmask_only(coordinates, data_filter_s2)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals2features', 
                        params = params, data = data, headers = headers)

    print(f"process id {pid}: {res.text}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return "set_invalid"

    print(f"files: {res.json()}")

    return "tasks_completed"


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


def send_request(bands, direction, pid, **kwargs):
    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    interval_size = get_data_from_payload("interval_size", int, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)
   
    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)

    data_filter_s1 = get_data_from_payload("data_filter_s1", str, True, **kwargs)

    path_prefix = "cfs/" + pu

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    headers = {'Content-Type': 'application/json'}

    params = {"process_id": pid, "data_source": "scihub", "resolution": "10", "path_prefix": path_prefix, 
              "start_date": start_date, "end_date": end_date, "aoi_coverage": aoi_coverage, "epsg": epsg, 
              "to_upload": True, "use_cache": use_cache, "orbit_direction": direction.upper()}

    if kwargs['task_instance'].try_number > 3:
        params["use_cache"] = "False"
        print("use_cache has been set to false")
    print(f"full params: {params}")

    data = create_calc_feat_data(start_date, end_date, bands, interval_size, coordinates, data_filter_s1, False)
    print(f"full data: {data}")

    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals1features', 
                        params = params, data = data, headers = headers)

    print(f"process id {pid} {direction}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_featurecalculation_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    data_found = True
    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        data_found = False
        return data_found

    print(f"files {direction}: {res.json()}")
    return data_found


def create_calc_feat_data(start_date, end_date, bands, interval_size, coordinates, data_filter=None, use_fmask=False):
    print(f"all params: start date: {start_date}, end date: {end_date}, interval size: {interval_size}, coordinates: {coordinates}, data filter: {data_filter}")

    features = create_features(start_date, end_date, interval_size, bands)
    if use_fmask:
        features["Fmask4"] = {"values": ["COUNT"]}
    print(f"features: {features}")

    if data_filter:
        data = {"aoi": coordinates, "features": features, "data_filter": json.loads(data_filter)}
    else:
        data = {"aoi": coordinates, "features": features}
    
    data = json.dumps(data)
    return data


def create_features(start_date, end_date, interval_size, bands):
    print(f"all bands: {bands}")
    features = {}
    for band in bands:
        features[band] = {"INTRPL":{"start_date": start_date, "end_date": end_date, "interval_size": interval_size, 
                          "file_format": "tiff"}}
    return features


def create_data_fmask_only(coordinates, data_filter=None):
    print("no bands except fmask4")
    features = {"Fmask4": {"values": ["COUNT"]}}
    print(f"features: {features}")

    if data_filter:
        data = {"aoi": coordinates, "features": features, "data_filter": json.loads(data_filter)}
    else:
        data = {"aoi": coordinates, "features": features}
    
    data = json.dumps(data)
    return data


dag = DAG(
    "feature_calculation_dag",
    default_args=default_args,
    description='feature calculation dag',
    schedule_interval=None,
    on_failure_callback=failure,
    #on_success_callback=success,
    max_active_runs=5,
    concurrency=5,
)

dag.doc_md = """
#### DAG Summary
Pipeline to calculate features.
"""

status = PythonOperator(task_id=f"status",
    provide_context=True,
    python_callable=state_function,
    dag=dag)

grid = PythonOperator(task_id=f"grid",
    provide_context=True,
    python_callable=call_grid_service,
    dag=dag)

calcfeat_s1 = BranchPythonOperator(task_id=f"calcfeat_temporals1features",
    provide_context=True,
    python_callable=call_calc_feature_s1,
    trigger_rule="none_failed",
    dag=dag)

calcfeat_s2 = BranchPythonOperator(task_id=f"calcfeat_temporals2features",
    provide_context=True,
    python_callable=call_calc_feature_s2,
    trigger_rule="none_failed",
    dag=dag)

calcfeat_pre = BranchPythonOperator(task_id=f"calcfeat_pre_calculated_features",
    provide_context=True,
    python_callable=call_calc_feature_pre,
    trigger_rule="none_failed",
    dag=dag)

fmask4 = BranchPythonOperator(task_id=f"calcfeat_dsl_only",
    provide_context=True,
    python_callable=call_fmask4,
    trigger_rule="none_failed",
    dag=dag)

tasks_completed = DummyOperator(task_id="tasks_completed",
    trigger_rule="none_failed",
    dag=dag)

set_invalid = PythonOperator(task_id=f"set_invalid",
    provide_context=True,
    python_callable=set_invalid,
    trigger_rule="none_failed",
    dag=dag)

finished = PythonOperator(task_id="finished", 
    provide_context=True,
    python_callable=success,
    dag=dag)

status >> grid >> calcfeat_s1 >> set_invalid
calcfeat_s1 >> calcfeat_s2 >> set_invalid
calcfeat_s2 >> calcfeat_pre >> set_invalid
calcfeat_pre >> tasks_completed
calcfeat_pre >> fmask4 >> set_invalid
fmask4 >> tasks_completed
tasks_completed >> finished
