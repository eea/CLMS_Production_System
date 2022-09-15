import json
import sys
from datetime import timedelta
import datetime
import os
import re
import shutil
import airflow
import fileinput
import subprocess as sp
from warnings import warn

import requests
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from joblib import Parallel, delayed
from joblib import parallel_backend
from glob import glob
import boto3
import rasterio

from airflow import DAG
from airflow.models import Variable
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.bash_operator import BashOperator
from geoville_ms_dag_state.dag_state import *
from geoville_ms_data_explorer import data_explorer
from geoville_storage_gate.raster import *
from geoville_storage_gate.netCDF import get_group_names
from sentinelsat import SentinelAPI, SentinelAPIError, SentinelAPILTAError, InvalidChecksumError

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
    'queue': 'harmonics',
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
SERVICE = "harmonics"
TAG = Variable.get('TAG')

# MOUNTS
m0 = "/mnt/files/settings/database.ini:/mnt/files/settings/database.ini"
# can be removed as soon as data finder/getter/preparer are modular and services itself
m1 = "/eodc:/eodc"
m2 = "/mnt/interim/{{ run_id }}:/interim"
m3 = "/mnt/out/" + SERVICE + ":/out"
m6 = "/mnt/interim/{{ run_id }}/output:/out"

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
    #success_dag(context['dag_run'].run_id, "/mnt/out/{}.nc".format(context['dag_run'].conf['service_name']))


def state_function(**context):
    running_dag(context['run_id'])


def get_date_since_begin(begin, scene):
    match = re.search(r'\d{4}/\d{1,2}/\d{1,2}', scene)
    date_from_str = match.group()
    date_from_str = date_from_str.split('/')
    date_from_str_obj = datetime.datetime(int(date_from_str[0]), int(date_from_str[1]), int(date_from_str[2]))

    date_array = begin.split('-')
    date_begin = datetime.datetime(int(date_array[0]), 1, 1)

    delta = (date_from_str_obj - date_begin).days
    return delta


def get_band(name):
    sql = "SELECT  band " \
          "FROM indices.sentinel_bands  as a " \
          "WHERE name = '" + str.upper(name) + "'"

    result = read_from_database_one_row(sql,
                                        None,
                                        os.getenv('DATABASE_CONFIG_FILE'),
                                        os.getenv('DATABASE_CONFIG_FILE_SECTION'),
                                        False)
    if result is None:
        return None
    return result[0]


def download_s3(band, res, days_count, key_band, path_out, esa_product_id):
    print("BAND: ", band)
    print(key_band)

    endpoint = "cf2.cloudferro.com:8080"
    region = "eu-west-1"
    tiled = "YES"
    if res == 10:
        blocksize = 512
    elif res == 20:
        blocksize = 256
    else:
        raise AttributeError("No valid resolution. Choose 10 or 20 meter.")
    bucket = "TAS-SentinelProducts"
    download_path = '{0}/{1}_{2}.tif'.format(path_out, days_count, band)
    aws_path_elements = key_band.split("/")
    print("ESA PRODUCT ID: ", esa_product_id)
#    esa_product_id = esa_product_id.split("_")[2]
#
#    # USING S3CMD ------------------------------------
#    if band == "Fmask4":
#        ending = '{}_Fmask4.tif'.format(esa_product_id, aws_path_elements[-1][:-4])
#    else:
#        ending = '{}_{}_{}m.tif'.format(esa_product_id, aws_path_elements[-1][:-4], res)
#    print("s3cmd --recursive la s3://TAS-SentinelProducts/ | awk '{{ print $4 }}' | grep 's2/cog/{}/{}/{}/{}/{}/{}' | grep 'Corrected' | grep '{}_{}_{}m.tif'".format(aws_path_elements[1], aws_path_elements[2], aws_path_elements[3], aws_path_elements[4], aws_path_elements[5].zfill(2), aws_path_elements[6].zfill(2), esa_product_id, aws_path_elements[-1][:-4], res))
#    #s3cmd_ls = sp.Popen("s3cmd --recursive la s3://TAS-SentinelProducts/ | awk '{{ print $4 }}' | grep 's2/cog/{}/{}/{}/{}/{}/{}' | grep 'Corrected' | grep '{}_{}_{}m.tif'".format(aws_path_elements[1], aws_path_elements[2], aws_path_elements[3], aws_path_elements[4], aws_path_elements[5].zfill(2), aws_path_elements[6].zfill(2), esa_product_id, aws_path_elements[-1][:-4], res),
#    #                    shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding="UTF-8")
#    s3cmd_ls = sp.Popen("s3cmd --recursive la s3://TAS-SentinelProducts/ | awk '{{ print $4 }}' | grep 's2/cog/{}/{}/{}/{}/{}/{}' | grep 'Corrected' | grep '{}_{}_{}m.tif'".format(aws_path_elements[1], aws_path_elements[2], aws_path_elements[3], aws_path_elements[4], aws_path_elements[5].zfill(2), aws_path_elements[6].zfill(2), ending),
#                        shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding="UTF-8")
#    sentinel_paths, s3cmd_ls_error = s3cmd_ls.communicate()
#    if s3cmd_ls_error:
#        raise Exception("s3cmd ls failed")
#
#    sentinel_paths = sentinel_paths.split("\n")
#    print("PATHS FOR ID: ", sentinel_paths)
#    sentinel_path = sentinel_paths[0]
#    sentinel_path = sentinel_path.replace("s3:/", "/vsis3")

    # USING PATH CONCAT
    if band == "Fmask4":
        filename = "_".join(["T"+aws_path_elements[1]+aws_path_elements[2]+aws_path_elements[3],
                             esa_product_id.split("_")[2],
                             "Fmask4.tif"])
    else:
        filename = "_".join(["T"+aws_path_elements[1]+aws_path_elements[2]+aws_path_elements[3],
                             esa_product_id.split("_")[2],
                             aws_path_elements[-1][:-4],
                             str(res)+"m.tif"])
    sentinel_path = "/vsis3/TAS-SentinelProducts/CLCplus/{}/{}/{}/{}/{}/{}/{}/{}".format(aws_path_elements[1],
                                                                                         aws_path_elements[2],
                                                                                         aws_path_elements[3],
                                                                                         aws_path_elements[4],
                                                                                         aws_path_elements[5].zfill(2),
                                                                                         aws_path_elements[6].zfill(2),
                                                                                         esa_product_id,
                                                                                         filename
                                                                                         )

    #if not sentinel_path:
    #    warn("{} does not exist on CREODIAS".format(key_band), ResourceWarning)
    #    return None

    nodata_setting = ""
    if band == "Fmask4":
        nodata_setting = "-a_nodata none"

    cmd = "gdal_translate {} -of GTiff --config AWS_VIRTUAL_HOSTING {} --config AWS_S3_ENDPOINT {} --config AWS_REGION {} --config AWS_SECRET_ACCESS_KEY {} --config AWS_ACCESS_KEY_ID {} " \
          "-co TILED={} -co BLOCKYSIZE={} -co BLOCKXSIZE={} " \
          "{} {}".format(nodata_setting, False, endpoint, region, os.getenv('AWS_KEY'), os.getenv('AWS_ID'), tiled, blocksize, blocksize, sentinel_path, download_path)
    print(cmd)
    gdal_dl = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding="UTF-8")
    gdal_dl_out, gdal_dl_error= gdal_dl.communicate()
    if gdal_dl_error:
        warn("gdal_translate failed. File/Date probably not available on CREODIAS: {}".format(gdal_dl_error), ResourceWarning)
        return None

    return '/interim/{0}_{1}.tif'.format(days_count, band)


def write_param_file(text, path_out, param):
    for line in fileinput.FileInput('{0}/harmonics_param.txt'.format(path_out), inplace=1):
        if param in line:
            line = line.rstrip()
            line = line.replace(line, "{0} {1}\n".format(line, text))
        sys.stdout.write(line)


def download_scene(aws_path, esa_product_id, band_name, optional_band_name, res, begin, path_out):
    key = aws_path.replace('s3://sentinel-s2-l2a/', '')
    band = get_band(band_name)
    key_band = key + 'R{0}m/{1}.tif'.format(res, band)
    days_count = get_date_since_begin(begin, aws_path)

    path = download_s3(band, res, days_count, key_band, path_out, esa_product_id)
    if not path:
        return None
    write_param_file(path, path_out, '--bands')
    write_param_file(days_count, path_out, '--time')

    #key_band = key + 'R20m/SCL.tif'
    key_band = key + 'R20m/Fmask4.tif'
    #scl = download_s3("SCL", 20, days_count, key_band, path_out, esa_product_id)
    scl = download_s3("Fmask4", 20, days_count, key_band, path_out, esa_product_id)
    write_param_file(scl, path_out, '--weights')

    band = get_band(optional_band_name)
    if band is not None:
        key_band = key + 'R{0}m/{1}.tif'.format(res, band)
        path_ndi = download_s3(band, res, days_count, key_band, path_out, esa_product_id)
        write_param_file(path_ndi, path_out, '--ndi')
    else:
        for line in fileinput.FileInput('{0}/harmonics_param.txt'.format(path_out), inplace=1):
            if "--ndi" in line:
                line = ""
            sys.stdout.write(line)


def get_tiles(**context):
    TILE = context['dag_run'].conf['tile_id']
    START = context['dag_run'].conf['start_date']
    END = context['dag_run'].conf['end_date']
    LEVEL = "L2A"
    BEARER = "Bearer " + Variable.get('BEARER')
    API = Variable.get('API')

    headers = {"accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": BEARER}
    url = "{}/data_explorer/sentinel_2/" \
          "tile/{}/date_range/{}/{}?processing_level={}".format(API, TILE, START, END, LEVEL)

    req = requests.get(url, headers=headers)
    resp = json.loads(req.text)

    # Get uuid's for the download
    ids = []
    ids_temp = {}
    date_temp = None
    for image in resp["response"]["images"]:
        date_temp = image["sensing_time"][0:7]

        # HERE DO YOUR FILTERING ---------------------------------------------------------------------------------
        #quality_score = (1 - image["cloud_percentage"] / 100) * (image["data_coverage_percentage"] / 100)
        #if image["aws_path"] is None:
        #    print("Image has no aws_path: " + image["uuid"])
        #    continue
        #print("Image: " + image["aws_path"])
        #print(date_temp)
        #print(quality_score)
        #if date_temp in ids_temp:
        #    if len(ids_temp[date_temp]) > 2:
        #        key = min(ids_temp[date_temp], key=ids_temp[date_temp].get)
        #        if ids_temp[date_temp][key] < quality_score:
        #            ids_temp[date_temp][image["aws_path"]] = quality_score
        #            ids_temp[date_temp].pop(key)
        #    else:
        #        ids_temp[date_temp][image["aws_path"]] = quality_score
        #else:
        #    ids_temp[date_temp] = {image["aws_path"]: quality_score}

        # ---------------------------------------------------------------------------------------------------------
        quality_score = 90
        if image["cloud_percentage"] <= quality_score:
            ids.append(image["aws_path"])

    #print(ids_temp)
    #for date in ids_temp:
    #    for key in ids_temp[date]:
    #        ids.append(key)
    print(ids)

    esa_product_ids = []
    for id in ids:
        for image in resp["response"]["images"]:
            if image["aws_path"] == id:
                esa_product_ids.append(image["esa_product_id"])

    print(ids)

    # create download directory for each tile
    out_dir = "/mnt/interim/{}".format(context['dag_run'].run_id)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # Download
    res = context['dag_run'].conf['resolution']
    if res == 10:
        blocksize = 512
    elif res == 20:
        blocksize = 256
    else:
        raise AttributeError("No valid resolution. Choose 10 or 20 meter.")
    with open('{0}/harmonics_param.txt'.format(out_dir), 'w') as file:
        file.writelines(["--bands", "\n--ndi", "\n--weights", "\n--time", "\n--blocksize {} {} ".format(blocksize, blocksize)])

    for i, pi in zip(ids, esa_product_ids):
        download_scene(i,
                       pi,
                       context['dag_run'].conf['band'],
                       context['dag_run'].conf['ndi_band'],
                       res,
                       context['dag_run'].conf['start_date'],
                       out_dir)


def get_representative_date(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    timedelta_days = (end_date - start_date).days
    representative_date = start_date + timedelta(days=timedelta_days/2)
    return datetime.datetime.strftime(representative_date, "%Y-%m-%d")


def write_into_storage_gate(**context):

    ncdf_output_path = "/mnt/out/{}.nc".format(context['dag_run'].conf['service_name'])
    output_path = "/mnt/interim/{}/output".format(context['dag_run'].run_id)
    for file in os.listdir(output_path):
        geotiff_input_path = os.path.join(output_path, file)

        with rasterio.open(geotiff_input_path) as src:
            array = src.read()
            print(array.shape)
            profile = src.profile
            print(profile)

        profile.update(start_date=context['dag_run'].conf['start_date'],
                       end_date=context['dag_run'].conf['end_date'],
                       band=context['dag_run'].conf['band'],
                       ndi_band=context['dag_run'].conf['ndi_band'],
                       user_id=context['dag_run'].conf['user_id'],
                       order_id=context['dag_run'].run_id)
        print(profile)

        representative_date = get_representative_date(context['dag_run'].conf['start_date'], context['dag_run'].conf['end_date'])

        if not os.path.exists(ncdf_output_path):
            print("Create new netCDF file")
            create_by_group(array,
                            profile,
                            ncdf_output_path,
                            context['dag_run'].conf['tile_id'],
                            representative_date,
                            representative_date,
                            array_variable=file.split(".")[0])
        else:
            print("Write into already existing netCDF file")
            existing_groups = get_group_names(ncdf_output_path)
            print(existing_groups)
            if context['dag_run'].conf['tile_id'] in existing_groups:
                print("Upsert existing group")
                upsert_by_group(array,
                                profile,
                                ncdf_output_path,
                                context['dag_run'].conf['tile_id'],
                                representative_date,
                                representative_date,
                                array_variable=file.split(".")[0])
            else:
                print("Create new group")
                create_by_group(array,
                                profile,
                                ncdf_output_path,
                                context['dag_run'].conf['tile_id'],
                                representative_date,
                                representative_date,
                                array_variable=file.split(".")[0])


dag = DAG(
    'harmonics',
    default_args=default_args,
    description='Harmonics DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    on_success_callback=success,
    #max_active_runs=1,
)

#t1 = BashOperator(
#    task_id='harmonics_hetzner_mount',
#    bash_command='mkdir /mnt/interim/{{ run_id }}; mkdir /mnt/interim/{{ run_id }}/output; chmod -R 777 /mnt/interim/{{ run_id }}',
#    dag=dag,
#)

t2 = PythonOperator(
    task_id='harmonics_state',
    python_callable=state_function,
    provide_context=True,
    dag=dag,
)

#t3 = PythonOperator(
#    task_id='harmonics_get_data',
#    python_callable=get_tiles,
#    provide_context=True,
#    dag=dag
#)

#t4 = BashOperator(
#    task_id='harmonics_add_config_file',
#    bash_command='cat /home/geoville/harmonics_config.txt >> /mnt/interim/{{ run_id }}/harmonics_param.txt;',
#    dag=dag,
#)

#t5 = DockerOperator(
#    task_id='harmonics',
#    image='imagehub.geoville.com/geoville_ms_harmonics:{}'.format(TAG),
#    command='./call_seasonality.sh /interim/harmonics_param.txt && chmod -R 777 /out',
#    volumes=[m2, m6],
#    network_mode="host",
#    xcom_push=True,
#    dag=dag,
#)

##t6 = PythonOperator(
##    task_id='harmonics_data_push',
##    python_callable=write_into_storage_gate,
##    provide_context=True,
##    dag=dag,
##)

##t7 = BashOperator(
##    task_id='harmonics_remove_interim',
##    bash_command='rm -r /mnt/interim/{{ run_id }}',
##    dag=dag,
##)

test = BashOperator(
    task_id='harmonics_test',
    bash_command='sleep 5',
    dag=dag,
)

#t1 >> t2 >> t3 >> t4 >> t5
t2 >> test
