import json
import shutil
import airflow
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from geoville_ms_dag_state.dag_state import *

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['IT-Services@geoville.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'queue': 'task1_stitching',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

# config
SERVICE = "stitching"


def failure(context):
    shutil.rmtree("/mnt/interim/{}".format(context['dag_run'].run_id), ignore_errors=True)
    failed_dag(context['dag_run'].run_id)


def success(context):
    success_dag(context['dag_run'].run_id, "/mnt/interim/{}".format(context['dag_run'].run_id))


def state_function(**context):
    running_dag(context['run_id'])


dag = DAG(
    'task1_stitching_dag',
    default_args=default_args,
    description='Stitching DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    on_success_callback=success,
    max_active_runs=1,
)

t1 = PythonOperator(
    task_id='stitching_state',
    python_callable=state_function,
    provide_context=True,
    dag=dag,
)

t2 = BashOperator(
    task_id='download_data',
    bash_command='/c/Windows/System32/cmd.exe /c/Users/clcplus/Documents/Script/download_data.bat {{dag_run.conf["processing_unit_name"]}},{{dag_run.conf["surrounding_pus"]}}',
    dag=dag
)

t3 = BashOperator(
    task_id='run_stitching',
    bash_command='bash /c/Users/clcplus/Documents/Script/run_stitching.sh -s {{dag_run.conf["processing_unit_name"]}} -r "{{dag_run.conf["surrounding_pus"]}}"',
    dag=dag,
)

t4 = BashOperator(
    task_id='upload_data',
    bash_command='/c/Windows/System32/cmd.exe /c/Users/clcplus/Documents/Script/upload_data.bat {{dag_run.conf["processing_unit_name"]}},{{dag_run.conf["surrounding_pus"]}}',
    dag=dag,
)

t1 >> t2 >> t3 >> t4
