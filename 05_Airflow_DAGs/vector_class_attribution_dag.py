import shutil
from datetime import timedelta
import datetime
import os
import airflow

from geoville_ms_dag_state.dag_state import *

from airflow import DAG
from airflow.models import Variable
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
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
    'queue': 'vector',
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
SERVICE = "vector_class_attribution"

# MOUNTS
# can be removed as soon as data finder/getter/preparer are modular and services itself
m1 = "/mnt/interim/{{ run_id }}:/interim"

# logger environment
logger_env = {'LOGGER_QUEUE_NAME': os.getenv('LOGGER_QUEUE_NAME'),
              'DATABASE_CONFIG_FILE': os.getenv('DATABASE_CONFIG_FILE'),
              'DATABASE_CONFIG_FILE_SECTION': os.getenv('DATABASE_CONFIG_FILE_SECTION'),
              'RABBIT_MQ_USER': os.getenv('RABBIT_MQ_USER'),
              'RABBIT_MQ_PASSWORD': os.getenv('RABBIT_MQ_PASSWORD'),
              'RABBIT_MQ_VHOST': os.getenv('RABBIT_MQ_VHOST')
              }


def failure(context):
    shutil.rmtree("/mnt/interim/{}".format(context['dag_run'].run_id), ignore_errors=True)
    failed_dag(context['dag_run'].run_id)


def success(context):
    success_dag(context['dag_run'].run_id, "/mnt/interim/{}".format(context['dag_run'].run_id))


def state_function(**context):
    running_dag(context['run_id'])


dag = DAG(
    'vector_class_attribution_dag',
    default_args=default_args,
    description='Vector Class Attribution DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    on_success_callback=success,
    max_active_runs=10,
)

t1 = BashOperator(
    task_id='vector_class_attribution_mount',
    bash_command='mkdir /mnt/interim/{{ run_id }}; mkdir /mnt/interim/{{ run_id }}/output; chmod -R 777 /mnt/interim/{{ run_id }}',
    dag=dag,
)

t2 = PythonOperator(
    task_id='vector_class_attribution_state',
    python_callable=state_function,
    provide_context=True,
    dag=dag,
)

t3 = DockerOperator(
    task_id='vector_class_attribution_preprocessing',
    image='imagehub.geoville.com/geoville_ms_vector_class_attribution:production',
    command='python3 -u /clipper.py '
	    '--rasters {{ dag_run.conf["raster"] }} '
	    '-o /interim/output.vrt '
	    '-v {{ dag_run.conf["vector"] }}'
	    '{{ " --config " if dag_run.conf["config"] else "" }}'
        '{{ dag_run.conf["config"] if dag_run.conf["config"] else "" }}',
    volumes=[m1],
    network_mode="host",
    xcom_push=True,
    dag=dag,
)

t4 = DockerOperator(
    task_id='vector_class_attribution_polygon_extraction',
    image='imagehub.geoville.com/geoville_ms_polygon_extraction:production',
    command='bin/polygon_extraction '
 	    '-r /interim/output.vrt '
	    '-v {{ dag_run.conf["vector"] }} '
	    '-x /interim/rasterized.tif'
        '{{ " -s " if dag_run.conf["subproduction_unit_name"] else "" }}'
        '{{ dag_run.conf["subproduction_unit_name"] if dag_run.conf["subproduction_unit_name"] else "" }}'
        '{{ " --config " if dag_run.conf["config"] else "" }}'
        '{{ dag_run.conf["config"] if dag_run.conf["config"] else "" }}'
	    ' -m {{ dag_run.conf["method"] }}'
        '{{ " --na_value " if dag_run.conf["na_value"] else "" }}'
        '{{ dag_run.conf["na_value"] if dag_run.conf["na_value"] else "" }}'
        '{{ " -n " if dag_run.conf["col_names"] else "" }}'
        '{{ dag_run.conf["col_names"] if dag_run.conf["col_names"] else "" }}'
        '{{ " -p " if dag_run.conf["method_params"] else "" }}'
        '{{ dag_run.conf["method_params"] if dag_run.conf["method_params"] else "" }}'
	    ' -o /interim/output.csv '
	    '-i {{ dag_run.conf["id_column"] }} ',
    volumes=[m1],
    network_mode="host",
    xcom_push=True,
    dag=dag,
)

t5 = DockerOperator(
    task_id='vector_class_attribution_postprocessing',
    image='imagehub.geoville.com/geoville_ms_vector_class_attribution:production',
    command='python3 -u /postprocessing.py '
	    '-i /interim/output.csv '
	    '-v {{ dag_run.conf["vector"] }} '
	    '-m {{ dag_run.conf["method"] }} '
	    '-y {{ dag_run.conf["reference_year"] }} '
	    '{{ " --config " if dag_run.conf["config"] else "" }}'
        '{{ dag_run.conf["config"] if dag_run.conf["config"] else "" }}'
	    ' -r /interim/report.txt '
	    '-o /interim/output_processed.csv ',
    volumes=[m1],
    network_mode="host",
    xcom_push=True,
    dag=dag,
)

t6 = DockerOperator(
    task_id='vector_class_attribution_push_to_s3',
    image='imagehub.geoville.com/geoville_ms_vector_class_attribution:production',
    command='python3 -u /copy_to_s3.py '
	    '-i /interim/output.csv /interim/report.txt /interim/output_processed.csv '
	    '--config {{ dag_run.conf["config"] }} '
	    '-o {{ dag_run.conf["bucket_path"] }} ',
    volumes=[m1],
    network_mode="host",
    xcom_push=True,
    dag=dag,
)

t7 = BashOperator(
    task_id='vector_class_attribution_remove_interim',
    bash_command='rm -r /mnt/interim/{{ run_id }}',
    dag=dag,
)


t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7
