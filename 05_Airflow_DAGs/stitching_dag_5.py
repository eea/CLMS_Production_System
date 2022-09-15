from datetime import timedelta, datetime
import time
import airflow
import os
import json
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
import requests
import shutil
import copy
from uuid import uuid4
from airflow.exceptions import AirflowSkipException
from geoville_ms_dag_state.dag_state import * 
from geoville_ms_logging.geoville_ms_logging import *

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2021, 6, 15),  # update this whenever DAG gets restarted
    'email': ['elena.jung@gaf.de', 'sooyeon.chun@gaf.de'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 6,
    'retry_delay': timedelta(minutes=1),
    'queue': 'stitching_queue_5', 
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    'wait_for_downstream': False,
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


def success(context):
    success_dag(context['dag_run'].run_id, "success")


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


def call_postprocessing_1(**kwargs):
    time.sleep(10)
    #time.sleep(40)
    pid = f"{kwargs['dag_run'].run_id}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    res = requests.get('http://post-processing.task-1-production:5000/postprocessing', params = {"process_id": pid})
    print(f"process id: {pid} - {res.text}")

    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_stitching_5_{kwargs['task_instance'].task_id}")
    
    if res.status_code == 204:
        print("nothing found to stitch")
        raise AirflowSkipException

    res.raise_for_status()
    kwargs['ti'].xcom_push(key='custom_aoi', value=res.json()["custom_aoi"])
    kwargs['ti'].xcom_push(key='bounding_box', value=res.json()["bounding_box"])
    kwargs['ti'].xcom_push(key='calc_feat_params', value=res.json()["calc_feat_params"])
    kwargs['ti'].xcom_push(key='calc_feat_data', value=res.json()["calc_feat_data"])
    kwargs['ti'].xcom_push(key='gaf_seg_params', value=res.json()["gaf_seg_params"])
    kwargs['ti'].xcom_push(key='gaf_seg_data', value=res.json()["gaf_seg_data"])


def call_calc_feature(**kwargs):
    pid = f"{kwargs['dag_run'].run_id}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    ti = kwargs['ti']
    params = ti.xcom_pull(key='calc_feat_params', task_ids='postprocessing_1')
    params["process_id"] = pid
    params["path_prefix"] = "task1_stitching"
    params["use_cache"] = False  # True
    
    if kwargs['task_instance'].try_number > 4:
        params["use_cache"] = False
        print(f"use_cache has been set to false: {params}")

    print(f"params {params}")
    
    calc_feat_data = ti.xcom_pull(key='calc_feat_data', task_ids='postprocessing_1')
    print(f"calc_feat_data {calc_feat_data}")

    #if kwargs['task_instance'].try_number > 2:
    calc_feat_data["data_filter"]["min_aoi_coverage"] = 0
    print(f"min aoi coverage has been set to 0")

    features = calc_feat_data["features"]

    pre_calc_feats = []
    feat_dict = {}
    for feat in features:
        feat = feat.strip()
        if not feat:
            continue
        if feature_is_pre_calculated(feat):
            pre_calc_feats.append(feat)
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
    calc_feat_data["features"] = feat_dict
    print(f"features dictionary: {calc_feat_data}")

    if not feat_dict:
        kwargs['ti'].xcom_push(key='calc_feat_params', value=params)
        kwargs['ti'].xcom_push(key='pre_calc_feats', value=pre_calc_feats)
        return

    coordinates = ti.xcom_pull(key='bounding_box', task_ids='postprocessing_1')
    print(f"coordinates {coordinates}")

    calc_feat_data["aoi"] = coordinates
    data = json.dumps(calc_feat_data)
    print(f"data {data}")

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://cfs-task-1-prod.task-1-production:5000/temporals2features', 
    params = params, data = data, headers = headers)
    print(f"process id: {pid} - {res.text}")

    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_stitching_5_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        raise Exception(f"no images - error: {res.json()}")

    kwargs['ti'].xcom_push(key='files', value=res.json())
    kwargs['ti'].xcom_push(key='calc_feat_params', value=params)
    data = json.loads(data)
    data["features"] = features
    data = json.dumps(data)
    kwargs['ti'].xcom_push(key='calc_feat_data', value=data)
    kwargs['ti'].xcom_push(key='pre_calc_feats', value=pre_calc_feats)


def call_calc_feature_pre(**kwargs):
    pid = f"{kwargs['dag_run'].run_id}_{kwargs['task_instance'].try_number}"
    print(f"process id {pid}")

    ti = kwargs['ti']
    precalculated_features = ti.xcom_pull(key='pre_calc_feats', task_ids='calcfeat')
    print(f"precalculated_features: {precalculated_features}")
    if not precalculated_features:
        return

    calc_feat_params = ti.xcom_pull(key='calc_feat_params', task_ids='calcfeat')
    start_date = calc_feat_params.get("start_date", None)
    end_date = calc_feat_params.get("end_date", None)
    path_prefix = calc_feat_params.get("path_prefix", None)

    if not (start_date and end_date and path_prefix):
        print(f"start_date: {start_date}, end_date: {end_date}, path_prefix: {path_prefix}")
        raise Exception(f"either the start_date, end_date or path_prefix were None")

    params = {"process_id": pid, "resolution": "10", "path_prefix": path_prefix, "epsg": "3035", "to_upload": True}

    coordinates = ti.xcom_pull(key='bounding_box', task_ids='postprocessing_1')
    print(f"coordinates {coordinates}")

    data = {"aoi": coordinates, "features": precalculated_features}
    data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://cfs-task-1-prod.task-1-production:5000/pre_calculated_features', 
                        params = params, data = data, headers = headers)
    print(f"process id {pid}: {res.text}")
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task2_stitching_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        raise Exception(f"no images - error: {res.json()}")

    files = res.json()["results"][0]["data"]
    print(f"files: {files}")
    ti.xcom_push(key="pre_calc_files", value=files)


def call_gaf_seg(**kwargs): 
    ti = kwargs['ti']

    results_from_calc_feature = ti.xcom_pull(key='files', task_ids='calcfeat') or {}
    try:
        calc_feat_data_files = results_from_calc_feature["results"][0]["data"]
    except KeyError:
        calc_feat_data_files = {}

    print(f"files from calc feat: {calc_feat_data_files}")
    
    calc_feat_data = ti.xcom_pull(key='calc_feat_data', task_ids='postprocessing_1')
    print(f"calc_feat_data {calc_feat_data}")
    
    files_pre_calc_feature = ti.xcom_pull(key='pre_calc_files', task_ids='calcfeat_pre_calculated_features')
    print(f"data from pre calc feat: {files_pre_calc_feature}")
    if files_pre_calc_feature:
        calc_feat_data_files.update(files_pre_calc_feature)
        print(f"files from calc feat and pre calc: {calc_feat_data_files}")

    features = calc_feat_data["features"]
    files = filenames_from_dict(calc_feat_data_files, features)

    data = ti.xcom_pull(key='gaf_seg_data', task_ids='postprocessing_1')
    print(f"data {data}")
    data["image_paths"] = files
    custom_aoi = ti.xcom_pull(key='custom_aoi', task_ids='postprocessing_1')
    print(f"custom_aoi {custom_aoi}")
    data["custom_aoi"] = custom_aoi
    print(f"data {data}")

    params = ti.xcom_pull(key='gaf_seg_params', task_ids='postprocessing_1')
    params["process_id"] = kwargs['dag_run'].run_id
    params["use_aoi"] = True
    params["is_stitching"] = True
    #data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}
    res = requests.post("http://gafseg-task-1-prod.task-1-production:5000/segmentation", params = params, json = data, headers = headers)
    print(f"process id: {kwargs['dag_run'].run_id} - {res.text}")

    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_stitching_5_{kwargs['task_instance'].task_id}")

    res.raise_for_status()

    kwargs['ti'].xcom_push(key='segmented_file', value=res.json())
    kwargs['ti'].xcom_push(key='gaf_seg_params', value=params)
    data.pop("custom_aoi")
    kwargs['ti'].xcom_push(key='gaf_seg_data', value=data)
    print(f"data after popping custom aoi: {data}")


def call_postprocessing_2(**kwargs):
    ti = kwargs['ti']
    result_from_gafseg = ti.xcom_pull(key='segmented_file', task_ids='gafseg')
    segmented_file = result_from_gafseg["result"]

    params = {"s3_key": segmented_file, "process_id": kwargs['dag_run'].run_id}

    headers = {'Content-Type': 'application/json'}
    calc_feat_params = ti.xcom_pull(key='calc_feat_params', task_ids='calcfeat') or {}
    calc_feat_data = ti.xcom_pull(key='calc_feat_data', task_ids='calcfeat') or {}
    gaf_seg_params = ti.xcom_pull(key='gaf_seg_params', task_ids='gafseg')
    gaf_seg_data = ti.xcom_pull(key='gaf_seg_data', task_ids='gafseg')
    data = {"calc_feat_data": json.loads(calc_feat_data),
            "calc_feat_params": calc_feat_params,
            "gaf_seg_data": gaf_seg_data,
            "gaf_seg_params": gaf_seg_params}
    data = json.dumps(data)

    res = requests.post('http://post-processing.task-1-production:5000/softbone', 
    params = params, headers = headers, data=data)
    print(f"{res.text}")
    
    if not res.ok:
        gemslog(LogLevel.ERROR, res.text, order_id=pid, service_name=f"task1_stitching_5_{kwargs['task_instance'].task_id}")
    
    res.raise_for_status()


dag = DAG(
    "task1_stitching_5",
    default_args=default_args,
    description='stitching dag offset by 40 seconds',
    schedule_interval=None,#'*/1 * * * *', #'*/1 0-15 * * *' if datetime.now().weekday() < 5 else '*/1 * * * *',  # UTC time (this is helpful to create the schedule: https://crontab.guru/) 16-23,0-9
    on_failure_callback=failure,
    on_success_callback=success,
    max_active_runs=15,
    concurrency=15,
    catchup=False,
)

dag.doc_md = """
#### DAG Summary
Pipeline to stitch the grids together for CLC+ Task 1.
"""

postprocessing_1 = PythonOperator(task_id=f"postprocessing_1",
    provide_context=True,
    python_callable=call_postprocessing_1,
    trigger_rule="none_failed",
    dag=dag)

calcfeat = PythonOperator(task_id=f"calcfeat",
    provide_context=True,
    python_callable=call_calc_feature,
    trigger_rule="none_failed",
    dag=dag)

calcfeat_pre = PythonOperator(task_id="calcfeat_pre_calculated_features",
    provide_context=True,
    python_callable=call_calc_feature_pre,
    trigger_rule="none_failed",
    dag=dag)

gafseg = PythonOperator(task_id=f"gafseg",
    provide_context=True,
    python_callable=call_gaf_seg,
    trigger_rule="none_failed",
    dag=dag)

postprocessing_2 = PythonOperator(task_id=f"postprocessing_2",
    provide_context=True,
    python_callable=call_postprocessing_2,
    trigger_rule="none_failed",
    dag=dag)


postprocessing_1 >> calcfeat >> calcfeat_pre >> gafseg >> postprocessing_2
