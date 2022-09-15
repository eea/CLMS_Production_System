import json
import sys
from datetime import timedelta
import datetime
import os
import airflow
from airflow.models import Variable
import psycopg2


from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['IT-Services@geoville.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'queue': 'state_order',
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

airflow_host = '45.130.31.43'
airflow_db = 'postgres'
airflow_user = 'postgres'
airflow_passwd = Variable.get('AIRFLOW_PASSWORD')

api_host = '45.130.31.218'
api_db = 'clcplus_backend'
api_user = 'postgres'
api_passwd = Variable.get('API_PASSWORD')

def query_airflow_db(order_ids, apidb_cursor_2, airflowdb_cursor, apidb_conn):

    sql_help_array = []
    results = {
        'failed': [],
        'success': []
    }

    for i in order_ids:
        sql_help_array.append('\'{}\''.format(i))

    get_airflowstatus_sql = 'SELECT run_id, state FROM public.dag_run WHERE run_id in ({})'.format(','.join(sql_help_array))
    #print(get_airflowstatus_sql)

    airflowdb_cursor.execute(get_airflowstatus_sql)
    for row in airflowdb_cursor:
        try:
            order_id = row[0]
            airflow_status = row[1]
            #print('order id: {}, airflow status: {}'.format(order_id, airflow_status))
            if airflow_status == 'failed':
                print('Setting status of {} to failed.'.format(order_id))
                results['failed'].append(order_id)
            elif airflow_status == 'success':
                print('Setting status of {} to success.'.format(order_id))
                results['success'].append(order_id)
            else:
                print('airflow status for order "{}" is "{}"'.format(order_id, airflow_status))
        except Exception as ex:
            print('exception with order {}: {}'.format(order_id, ex))

    #print(results)

    if len(results['failed']) > 0:
        sql_help_array = []
        print("FAILED:")
        for i in results['failed']:
            print(i)
            sql_help_array.append('\'{}\''.format(i))
        update_failed_sql = 'UPDATE customer.service_orders SET order_stopped = \'1999-01-01\', status = \'FAILED\' WHERE order_id in ({})'.format(','.join(sql_help_array))
        apidb_cursor_2.execute(update_failed_sql)
        print("---------------------------------------------")
        #print(apidb_cursor_2.statusmessage)
        #print(update_failed_sql)

    if len(results['success']) > 0:
        sql_help_array = []
        print("SUCCESS")
        for i in results['success']:
            print(i)
            sql_help_array.append('\'{}\''.format(i))
        update_success_sql = 'UPDATE customer.service_orders SET order_stopped = \'1999-01-01\', status = \'SUCCESS\' WHERE order_id in ({})'.format(','.join(sql_help_array))
        apidb_cursor_2.execute(update_success_sql, [])
        print("---------------------------------------------")
        #print(apidb_cursor_2.statusmessage)
        #print(update_success_sql)    

    apidb_conn.commit()

def retrigger(**context): 
    try:
        airflowdb_conn = psycopg2.connect(database=airflow_db, user=airflow_user, host=airflow_host, password=airflow_passwd)
        airflowdb_cursor = airflowdb_conn.cursor()
        print('airflow db connected successfully')


        apidb_conn = psycopg2.connect(database=api_db, user=api_user, host=api_host, password=api_passwd)
        apidb_cursor = apidb_conn.cursor()
        apidb_cursor_2 = apidb_conn.cursor()
        print('api db connected successfully')
    except Exception as ex:
        print('exception when connecting to db: {}'.format(ex))

    # find orders with status queued/running in api db

    get_problematic_orders_sql = """
        SELECT order_id, status FROM customer.service_orders 
        WHERE status IN ('QUEUED', 'RUNNING', 'RECEIVED') 
        AND order_received < NOW() - interval '1 HOUR'
    """

    apidb_cursor.execute(get_problematic_orders_sql)

    # look up each order in airflow db in batches
    counter = 0
    order_ids = []
    for row in apidb_cursor:
        counter += 1
        order_ids.append(row[0])
        if counter == 1000:
            query_airflow_db(order_ids, apidb_cursor_2, airflowdb_cursor, apidb_conn)
            counter = 0
            order_ids = []

    if len(order_ids) > 0:
        query_airflow_db(order_ids, apidb_cursor_2, airflowdb_cursor, apidb_conn)

    apidb_conn.close()
    airflowdb_conn.close()

dag = DAG(
    'state_order_retrigger_dag',
    schedule_interval='*/15 * * * *',
    default_args=default_args,
    description='Test DAG',
    max_active_runs=1,
    catchup=False,
)

t1 = PythonOperator(
    task_id='retrigger',
    python_callable=retrigger,
    provide_context=True,
    dag=dag,
)

t1
