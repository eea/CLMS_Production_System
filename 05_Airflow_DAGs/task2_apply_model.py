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
    'retries': 7,
    'retry_delay': timedelta(minutes=2),
    'queue': 'apply_model_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # wait_for_downstream': True,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(minutes=50),
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


def call_grid_service(**kwargs): 
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_applymodel"
    print(f"process id {pid}")

    res = requests.get("http://grid-service-prod-t2.task-2-production:80/eea_grid", params={"cell_code_input": pu, "process_id": pid})
    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")
    res.raise_for_status()
    kwargs['ti'].xcom_push(key='coordinates', value=res.json()["aoi"])
    kwargs['ti'].xcom_push(key='epsg', value=res.json()["epsg"])


def call_calc_feature(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_applymodel"
    print(f"process id {pid}")

    s1_bands = get_data_from_payload("s1_bands", list, True, **kwargs)
    if s1_bands and s1_bands[0]:
        is_data_valid = call_calc_feature_s1(s1_bands, pid, **kwargs)
        if not is_data_valid:
            return "set_invalid"
    else:
        print("no s1 bands requested")

    s2_bands = get_data_from_payload("s2_bands", list, True, **kwargs)
    if s2_bands and s2_bands[0]:
        is_data_valid = call_calc_feature_s2(s2_bands, pu, pid, **kwargs)
        if not is_data_valid:
            return "set_invalid"
    else:
        print("no s2 bands requested")

    precalculated_features = get_data_from_payload("precalculated_features", list, True, **kwargs)
    if precalculated_features and precalculated_features[0]:
        is_data_valid = call_calc_feature_pre(precalculated_features, pu, pid, **kwargs)
        if not is_data_valid:
            return "set_invalid"
    else:
        print("no pre calculated features requested")

    return "applymodel"


def call_calc_feature_s1(s1_bands, pid, **kwargs):
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
            gemslog(LogLevel.ERROR, f"{band} not in the correct format", order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")
            raise Exception(f"{band} not in the correct format. The correct format is 'DSC_band' or 'ASC_band'") 

    if bands_asc:
        data_found = send_request(bands_asc, "ascending", pid, **kwargs)
        if not data_found:
            return False

    if bands_dsc:
        data_found = send_request(bands_dsc, "descending", pid, **kwargs)
        if not data_found:
            return False
    
    return True

    
def call_calc_feature_s2(s2_bands, pu, pid, **kwargs):
    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    interval_size = get_data_from_payload("interval_size", int, False, **kwargs)
    cloud_cover = get_data_from_payload("cloud_cover", int, False, **kwargs)

    aoi_coverage = get_data_from_payload("aoi_coverage", int, True, **kwargs)
    
    use_cache = get_data_from_payload("use_cache", bool, False, **kwargs)

    data_filter_s2 = get_data_from_payload("data_filter_s2", str, True, **kwargs)

    path_prefix = "cfs/" + pu
    print(f"path prefix: {path_prefix}")

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')
    print(f"coordinates: {coordinates}")

    params = {"process_id": pid, "data_source": "wekeo_S2", "resolution": "10", "cloudmask_type": "Fmask4", 
              "path_prefix": path_prefix, "start_date": start_date, "end_date": end_date, "max_cloudcover": cloud_cover, "epsg": epsg, 
              "aoi_coverage": aoi_coverage, "to_upload": True, "use_cache": use_cache}

    if kwargs['task_instance'].try_number > 3:
        params["use_cache"] = "False"
        print(f"use_cache has been set to false")
    print(f"try_number: {kwargs['task_instance'].try_number}")
    print(f"full S2 params: {params}")

    if isinstance(s2_bands[0], list):
        s2_bands = s2_bands[0]
    print(f"s2_bands: {s2_bands}")

    data = create_calc_feat_data(start_date, end_date, s2_bands, interval_size, coordinates, data_filter_s2)
    print(f"full S2 data: {data}")

    headers = {'Content-Type': 'application/json'}
    
    print(f"calling temporals 2 features")
    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals2features', 
                        params = params, data = data, headers = headers)
    print(f"finished calling temporals 2 features")
    if len(res.text) < 20000:
        print(f"S2 process id {pid}: {res.text}")
    else:
        print(f"S2 process id {pid}: {res.status_code}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return False

    files = res.json()["results"][0]["data"]
    print(f"files: {files}")
    ti.xcom_push(key="temporal_files_s2", value=files)
    return True


def call_calc_feature_pre(precalculated_features, pu, pid, **kwargs):
    start_date = get_data_from_payload("start_date", str, False, **kwargs)
    end_date = get_data_from_payload("end_date", str, False, **kwargs)
    interval_size = get_data_from_payload("interval_size", int, False, **kwargs)

    path_prefix = "cfs/" + pu

    ti = kwargs['ti']
    epsg = ti.xcom_pull(key='epsg', task_ids='grid')

    params = {"process_id": pid, "resolution": "10", "path_prefix": path_prefix, "epsg": epsg, "to_upload": True}
    print(f"full pre calc feature params: {params}")

    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')

    if isinstance(precalculated_features[0], list):
        precalculated_features = precalculated_features[0]

    data = {"aoi": coordinates, "features": precalculated_features}
    data = json.dumps(data)
    print(f"full pre calc feature data: {data}")

    headers = {'Content-Type': 'application/json'}

    print(f"calling pre calculated features")
    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/pre_calculated_features', 
                        params = params, data = data, headers = headers)
    
    print(f"finished calling pre calculated features")
    if len(res.text) < 20000:
        print(f"pre calculated features process id {pid}: {res.text}")
    else:
        print(f"pre calculated features process id {pid}: {res.status_code}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        return False

    data = res.json()["results"][0]["data"]
    files = {}
    for band, file_data in data.items():
        if isinstance(file_data, str):
            files[band] = file_data
        elif isinstance(file_data, dict):
            files[band] = file_data["path"]
        else:
            raise Exception(f"file data is not a string or a dictionary: {type(file_data)}")
    print(f"files: {files}")
    ti.xcom_push(key="pre_calc_files", value=files)
    return True


def call_apply_model(**kwargs):
    pu = get_data_from_payload("processing_unit_name", str, False, **kwargs)
    pid = f"{kwargs['dag_run'].run_id}_{pu}_{kwargs['task_instance'].try_number}_applymodel"
    print(f"process id {pid}")

    ti = kwargs['ti']
    s1_files_asc = ti.xcom_pull(key='temporal_files_s1_ascending', task_ids='calcfeat')
    s1_files_dsc = ti.xcom_pull(key='temporal_files_s1_descending', task_ids='calcfeat')
    s2_files = ti.xcom_pull(key='temporal_files_s2', task_ids='calcfeat')
    
    if not (s1_files_asc or s1_files_dsc or s2_files):
        print("no s1 or s2 files")
        return "set_invalid"
    
    pre_calc_files = ti.xcom_pull(key='pre_calc_files', task_ids='calcfeat')
    
    metaclassifier = filenames_from_dict_pre_calc(pre_calc_files) if pre_calc_files else []
    
    files = []
    for temporal_dict in [s1_files_asc, s1_files_dsc, s2_files]:
        temporal_list = filenames_from_dict(temporal_dict) if temporal_dict else []
        files.extend(temporal_list)

    model_path = get_data_from_payload("model_path", str, False, **kwargs)

    data = {
        "inputs": {
        "metaclassifier": metaclassifier,
        "temporal": files
        }
    }

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    res = requests.post('http://apply-model-prod-t2.task-2-production:80/applymodel', 
    params = {"model_path": model_path, "process_id": pid}, data = json.dumps(data), headers=headers)
    
    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")
    res.raise_for_status()
    return "finished"


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
        print(f"use_cache has been set to false")
    print(f"full S1 params: {params}")
    
    data = create_calc_feat_data(start_date, end_date, bands, interval_size, coordinates, data_filter_s1)
    print(f"full S1 data: {data}")

    print(f"calling temporals 1 features")
    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals1features', 
                        params = params, data = data, headers = headers)
    
    print(f"finished calling temporals 1 features")
    if len(res.text) < 20000:
        print(f"S1 process id {pid} {direction}: {res.text}")
    else:
        print(f"S1 process id {pid} {direction}: {res.status_code}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_applymodel_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    data_found = True
    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        data_found = False
        return data_found

    files = res.json()["results"][0]["data"]
    print(f"files {direction}: {files}")
    kwargs['ti'].xcom_push(key=f"temporal_files_s1_{direction}", value=files)
    return data_found


def create_calc_feat_data(start_date, end_date, bands, interval_size, coordinates, data_filter=None):

    features = create_features(start_date, end_date, interval_size, bands)
    print(f"features: {features}")

    if data_filter:
        data = {"aoi": coordinates, "features": features, "data_filter": json.loads(data_filter)}
    else:
        data = {"aoi": coordinates, "features": features}
    data = json.dumps(data)
    return data


def create_features(start_date, end_date, interval_size, bands):
    features = {}
    for band in bands:
        features[band] = {"INTRPL":{"start_date": start_date, "end_date": end_date, "interval_size": interval_size, 
                          "file_format": "tiff"}}
    return features


def filenames_from_dict(files_dict):
    print(f"files_dict temporal: {files_dict}")
    files_as_list = []
    keys_sorted = list(files_dict.keys())
    keys_sorted.sort()
    for k in keys_sorted:
        files = files_dict[k]
        for metric, filepath in files.items():
            if metric == "INTRPL":
                files_as_list.append(filepath)
    print("all temporal files appended to list")
    return files_as_list


def filenames_from_dict_pre_calc(files_dict):
    print(f"files_dict pre_calc: {files_dict}")
    files_as_list = []
    keys_sorted = list(files_dict.keys())
    keys_sorted.sort()
    for k in keys_sorted:
        filepath = files_dict[k]
        files_as_list.append(filepath)
    print("all pre calculated files appended to list")
    return files_as_list


dag = DAG(
    "apply_model_dag",
    default_args=default_args,
    description='apply model dag',
    schedule_interval=None,
    on_failure_callback=failure,
    #on_success_callback=success,
    max_active_runs=32,
    concurrency=32,
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

calcfeat = BranchPythonOperator(task_id=f"calcfeat",
    provide_context=True,
    python_callable=call_calc_feature,
    trigger_rule="none_failed",
    dag=dag)

applymodel = BranchPythonOperator(task_id=f"applymodel",
    provide_context=True,
    python_callable=call_apply_model,
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
    trigger_rule="none_failed",
    dag=dag)


status >> grid >> calcfeat >> set_invalid
calcfeat >> applymodel >> set_invalid
applymodel >> finished
