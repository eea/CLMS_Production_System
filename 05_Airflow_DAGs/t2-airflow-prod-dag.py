from datetime import timedelta
import airflow
import os
import json
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
import requests
import shutil
import copy
from geoville_ms_dag_state.dag_state import * 


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
    'queue': 'task_2_dag_production',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    'wait_for_downstream': True,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(seconds=7200),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

def failure(context):
    failed_dag(context['dag_run'].run_id)


def success(context):
    success_dag(context['dag_run'].run_id, "success")


def state_function(**context):
    running_dag(context['run_id'])


#def failure(context):
#    print('failure')


#def success(context):
#    print('success')

def filenames_from_dict(files_dict):
    files_as_list = []
    keys_sorted = list(files_dict.keys())
    keys_sorted.sort()
    for k in keys_sorted:
        files_as_list.append(files_dict[k]['INTRPL'])
    print("all files appended to list")
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


def call_grid_service(**kwargs):
    print(f"process id {kwargs['dag_run'].run_id}")
    params = get_data_from_payload("grid_params", dict, False, **kwargs)

    res = requests.get("http://grid-service-prod-t2.task-2-production:80/eea_grid", params= params)
    print(f"process id {kwargs['dag_run'].run_id}: {res.text}")
    res.raise_for_status()
    print(res.json())
    kwargs['ti'].xcom_push(key='coordinates', value=res.json())


def call_calc_feature(**kwargs):
    print(f"process id {kwargs['dag_run'].run_id}")
    params = get_data_from_payload("calc_feat_params", dict, False, **kwargs)
    params["process_id"] = kwargs['dag_run'].run_id

    print(f"retry number: {kwargs['task_instance'].try_number}")
    if kwargs['task_instance'].try_number > 3:
        params["use_cache"] = "False"
        print(f"use_cache has been set to false: {params}")
    
    features = get_data_from_payload("calc_feat_data", dict, False, **kwargs)

    ti = kwargs['ti']
    coordinates = ti.xcom_pull(key='coordinates', task_ids='grid')

    data = copy.deepcopy(features)
    data["aoi"] = coordinates
    data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    res = requests.post('http://calc-feature-service-prod-t2.task-2-production:80/temporals2features', 
    params = params, data = data, headers = headers)
    print(f"process id {kwargs['dag_run'].run_id}: {res.text}")
    res.raise_for_status()
    if res.json()["code"] == 'NO_IMAGES':
        print(f"no images - error: {res.json()}")
        raise Exception("no images found") 
    print(f"result: {res.json()}")
    kwargs['ti'].xcom_push(key='files', value=res.json())


def call_apply_model(**kwargs):
    print(f"process id {kwargs['dag_run'].run_id}")
    ti = kwargs['ti']
    results_from_calc_feature = ti.xcom_pull(key='files', task_ids='calcfeat')
    calc_feat_data = results_from_calc_feature["results"][0]["data"]
    files = filenames_from_dict(calc_feat_data)
    print(f"files from calc feat: {files}")

    params = get_data_from_payload("apply_model_params", dict, False, **kwargs)
    params["process_id"] = kwargs['dag_run'].run_id
    metaclassifier = get_data_from_payload("apply_model_metaclassifier", list, False, **kwargs)

    data = {
        "inputs": {
        "metaclassifier": metaclassifier,
        "temporal": files
        }
    }

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    res = requests.post('http://apply-model-prod-t2.task-2-production:80/applymodel', 
    params = params, data = json.dumps(data), headers=headers)

    print(f"process id {kwargs['dag_run'].run_id}: {res.text}")
    res.raise_for_status()


dag = DAG(
    "task_2_dag_production",
    default_args=default_args,
    description='Task 2 Production DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    on_success_callback=success,
    max_active_runs=50,
    concurrency=50,
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

calcfeat = PythonOperator(task_id=f"calcfeat",
    provide_context=True,
    python_callable=call_calc_feature,
    dag=dag)
        
applymodel = PythonOperator(task_id=f"applymodel",
    provide_context=True,
    python_callable=call_apply_model,
    dag=dag)

status >> grid >> calcfeat >> applymodel
