from datetime import timedelta
import os
import gc
import shutil
import time
import boto3
import airflow
import pyproj
import shapely.wkt
from shapely.ops import transform
import xarray as xr
import geopandas as gpd
from affine import Affine
from shapely.geometry import mapping
from rioxarray.merge import merge_datasets
from airflow import DAG
from shapely import wkt
import subprocess as sp
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from geoville_ms_dag_state.dag_state import failed_dag, success_dag, \
    running_dag
from geoville_ms_database.geoville_ms_database import execute_database
from lib.storage_utils import get_raster_group_names_intersecting_bounds, \
    read_netcdf
from geoville_storage_gate.netCDF import get_group_names
import dask_geopandas


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
    'queue': 'get_product',
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

# logger environment
logger_env = {'LOGGER_QUEUE_NAME': os.getenv('LOGGER_QUEUE_NAME'),
              'DATABASE_CONFIG_FILE': os.getenv('DATABASE_CONFIG_FILE'),
              'DATABASE_CONFIG_FILE_SECTION':
                  os.getenv('DATABASE_CONFIG_FILE_SECTION'),
              'RABBIT_MQ_USER': os.getenv('RABBIT_MQ_USER'),
              'RABBIT_MQ_PASSWORD': os.getenv('RABBIT_MQ_PASSWORD'),
              'RABBIT_MQ_VHOST': os.getenv('RABBIT_MQ_VHOST')
              }

def update_status(order_id, status, result):
    """ Updates the service order status

    This method updates the service order table in the database by adding the correct status of the processing and the
    time stamp when the execution stopped.

    Arguments:
        order_id (str): current order ID
        status (str): status of the triggered service order
        result (str): result of the triggered service order

    """

    db_ini_file = os.environ.get("DATABASE_CONFIG_FILE")
    db_ini_section = os.environ.get("DATABASE_CONFIG_FILE_SECTION")

    sql = "UPDATE customer.service_orders SET status = %s, result = %s"
    values = [status, result]

    if status.lower() == 'success':
        sql += ', success = true, order_stopped = NOW()'

    elif status.lower() == 'failed':
        sql += ', success = false, order_stopped = NOW()'

    elif status.lower() == 'running':
        sql += ', order_started = NOW()'

    sql += " WHERE order_id = %s"
    values.append(order_id)

    execute_database(sql, values, db_ini_file, db_ini_section, True)


def failure(**context):
    shutil.rmtree("/mnt/interim/{}".format(context['dag_run'].run_id),
                  ignore_errors=True)
    update_status(context['dag_run'].run_id, 'FAILED', None)


def success(**context):
    result = context['task_instance'].xcom_pull(key="result",
                                                task_ids='upload_result')
    update_status(context['dag_run'].run_id, 'SUCCESS', result)


def state_function(**context):
    update_status(context['dag_run'].run_id, 'RUNNING', None)


def upload_result(**context):
    aws = \
        boto3.resource('s3',
                       region_name="eu-central-1",
                       aws_access_key_id="bc8e686837c2476ba4dcef06ba7272ca",
                       aws_secret_access_key="2e7516dc941f4bdcae1204d51c354bee",
                       endpoint_url="https://cf2.cloudferro.com:8080")

    bucket = aws.Bucket("clcplus-public")
    product_file = f"/mnt/interim/{context['dag_run'].run_id}/{context['dag_run'].conf['product']}_{context['dag_run'].run_id}.zip" # context['task_instance'].xcom_pull(key="return_value", task_ids='get_product')
    product_basename = os.path.basename(product_file)
    bucket.upload_file(product_file, f"products/{product_basename}")
    context['ti'].xcom_push(key="result",
                            value=f"https://s3.waw2-1.cloudferro.com/swift/v1/AUTH_b9657821e4364f88862ca20a180dc485/clcplus-public/products/{product_basename}")


def read_raster_by_bounds(input_ncdf, bounds):
    """
    takes 110 seconds for hungary
    old module gets memory error for hungary
    """
    ncdf_dataset = read_netcdf(input_ncdf)
    intersection = get_raster_group_names_intersecting_bounds(ncdf_dataset,
                                                              bounds)
    ncdf_dataset.close()
    if not intersection:
        raise Exception("The product does currently not intersect the given area")
    subsets = []
    print(f"{len(intersection)} intersections found")
    for g in intersection:
        print(g)
        ds = xr.open_dataset(input_ncdf, group=g,
                             chunks={"time": 1, "x": 1000, "y": 1000})
        xres, xskew, ulx, yskew, yres, uly, _, _, _ = ds.transform
        geotransformation = Affine(xres, xskew, ulx, yskew, yres, uly)
        ds_raster = ds.raster
        ds_raster = ds_raster.astype(ds.dtype)
        ds_raster.rio.write_crs(ds.crs, inplace=True)
        ds_raster.rio.write_transform(geotransformation, inplace=True)
        subset = ds_raster.rio.clip(
            gpd.GeoDataFrame(geometry=[bounds],
                             crs=ds.crs).geometry.apply(mapping),
            ds.crs)
        subset_ds = subset.to_dataset()
        subsets.append(subset_ds)
        del subset_ds
        gc.collect()

    merged = merge_datasets(subsets)
    return merged


def read_vector_by_bounds(input_ncdf, bounds, result_path):
    """
    takes 3207 seconds for hungary
    old code takes way too long (sick of waiting)
    """
    # get group name
    pu_shapefile = "/home/geoville/EEA39_eu_PU_ID_SPU_ID_v42_dissolve_3035.shp"
    pu_gdf = gpd.read_file(pu_shapefile)
    pus_intersecting_bounds = []
    pus_within_bounds = []
    
    #edited by the ninja team
    #print(bounds)

    for idx, row in pu_gdf.iterrows():

        #edited...
        #print(row['UNIQUE_ID'])

        if bounds.intersects(row["geometry"]):
            
            #print(row)

            ### changed row[PU_ID to UNIQUE_ID ###
            if row["geometry"].within(bounds):
                #print('within')
                pus_within_bounds.append(row["UNIQUE_ID"])
            else:
                #print('intersects')
                pus_intersecting_bounds.append(row["UNIQUE_ID"])

    #print(pus_intersecting_bounds)
    groups_of_netcdf = get_group_names(input_ncdf)
    #print(groups_of_netcdf)
    groups_intersect = [f"PU{pu}" for pu in pus_intersecting_bounds if f"PU{pu}" in groups_of_netcdf]
    groups_within = [f"PU{pu}" for pu in pus_within_bounds if f"PU{pu}" in groups_of_netcdf]

    if not groups_intersect and not groups_within:
        raise Exception("No data found for the given AOI")
    print("group names identified")

    final_result_paths = []
    for group in groups_intersect:
        print(group)

        df = xr.open_dataset(input_ncdf,
                             group=group,
                             chunks={"features": 1000}).to_dataframe()

        # df to gdf
        gdf = dask_geopandas.from_geopandas(gpd.GeoDataFrame(df,
                                                             geometry=df['geometry'].apply(wkt.loads),
                                                             crs="EPSG:3035"),
                                            npartitions=8)

        # intersection of gdf with bounds
        print(gdf.crs)

        intersection = gdf[gdf.intersects(bounds)] # gets all intersecting polygons
        intersection['geometry'] = intersection.buffer(0) # @JS: why?
        intersection = intersection.compute() # convert dask_geopandas GeoSeries to gpd.GeoDataFrame
        print(f"{120 * '-'}\nintersection = intersection.compute()\nGDF:")
        print(intersection)

        print(f"{120 * '-'}\nBounds wkt: {bounds.wkt}")
        print(f"Total extent bounds: {bounds.bounds}")
        print(f"Total extent GDF before clipping: {intersection.total_bounds}")
        # A valid Polygon may not possess any overlapping exterior or interior rings.
        # A valid MultiPolygon may not collect any overlapping polygons.
        print(f"Bounds valid: {bounds.is_valid}")
        print(f"Number of polygons in bounds: {len(bounds.geoms)}")
        print(f"Number of polygons in GDF before clipping: {len(intersection)}\n{120 * '-'}")
        print("sleep")
        time.sleep(300)
        print("sleep done")
        intersection = gpd.clip(intersection, bounds) # clips polygons along the boundary
        print(f"Total extent GDF after clipping: {intersection.total_bounds}")
        print(f"{120 * '-'}\nintersection = gpd.clip(intersection, bounds)\nGDF:")
        print(intersection)

        if intersection.empty:
            print("empty intersection")
            continue
        print("intersection done")

        result_path_part = result_path.replace(".gpkg", f"_{group}.gpkg")
        if not os.path.exists(result_path_part):
            intersection.to_file(result_path_part, driver="GPKG")
        final_result_paths.append(result_path_part)

    print("entire groups")
    for group in groups_within:
        print(group)

        df = xr.open_dataset(input_ncdf,
                             group=group,
                             chunks={"features": 1000}).to_dataframe()

        # df to gdf
        gdf = gpd.GeoDataFrame(df,
                               geometry=df['geometry'].apply(wkt.loads),
                               crs="EPSG:3035")

        result_path_part = result_path.replace(".gpkg", f"_{group}.gpkg")
        if not os.path.exists(result_path_part):
            gdf.to_file(result_path_part, driver="GPKG")
        final_result_paths.append(result_path_part)

    return final_result_paths


def create_dynamic_files(raster_path):
    tmp = raster_path.replace(".tif", "_tmp.tif")
    cmds = [f"gdal_translate {raster_path} "
            f"{tmp} -of HFA -co AUX=YES -co STATISTICS=YES",
            f"gdal_translate {raster_path} {tmp} -co TFW=YES",
            f"gdaladdo -ro --config COMPRESS_OVERVIEW LZW {tmp} 2 4 8 16"]
    for cmd in cmds:
        process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        _, err = process.communicate()
        if process.returncode != 0:
            raise Exception('CMD ({}) failed with: {}'.format(cmd, str(err)))
    os.rename(tmp.replace(".tif", ".tfw"), raster_path.replace(".tif", ".tfw"))
    os.rename(tmp+".ovr", raster_path+".ovr")
    os.remove(tmp)
    return [raster_path.replace(".tif", f"{ending}")
            for ending in [".tif.ovr", ".tif.aux.xml", ".tfw"]]


def get_product(**context):

    product = context['dag_run'].conf['product']
    reproject = pyproj.Transformer.from_crs(pyproj.CRS('EPSG:4326'),
                                            pyproj.CRS('EPSG:3035'),
                                            always_xy=True).transform
    aoi_geom = transform(reproject,
                         shapely.wkt.loads(context['dag_run'].conf['aoi']))
    ncdf_output_path = f"/mnt/products/{product}.nc"

    # retrieve data from netcdf -----------------------------------------------
    result_path = None

    if product == "Raster":
        result_path = \
            os.path.join("/mnt/interim", context['dag_run'].run_id,
                         f"{product}_{context['dag_run'].run_id}.tif")

        cropped_ds = read_raster_by_bounds(ncdf_output_path, aoi_geom)
        cropped_ds.raster.rio.to_raster(result_path, compress='LZW')

    if product == "Vector":
        result_path = \
            os.path.join("/mnt/interim", context['dag_run'].run_id,
                         f"{product}_{context['dag_run'].run_id}.gpkg")

        vector_result_paths = \
            read_vector_by_bounds(ncdf_output_path, aoi_geom, result_path)
        print("vector_result_paths: ", vector_result_paths)

    # Create ZIP with static and dynamic extra files --------------------------
    if product == "Raster":
        static_files = [os.path.join("/mnt/products", static)
                        for static in os.listdir("/mnt/products")
                        if static.endswith(('.xml',
                                            '.tif.clr',
                                            '.tif.vat.cpg',
                                            '.txt',
                                            '.qml'))
                        and "raster" in static.lower()]
        dynamic_files = create_dynamic_files(result_path)

    elif product == "Vector":
        static_files = [os.path.join("/mnt/products", static)
                        for static in os.listdir("/mnt/products")
                        if static.endswith(('.xml',
                                            '.sld'))
                        and "vector" in static.lower()]
        dynamic_files = []

    else:
        static_files = []
        dynamic_files = []

    all_files = static_files + dynamic_files

    if product == "Raster":
        zip_path = result_path.split(".")[0]
        os.makedirs(zip_path)
        for af in all_files:
            ending = ".".join(af.split(".")[1:])
            shutil.copy(af, os.path.join(zip_path, os.path.basename(zip_path)
                                         + "." + ending))
        shutil.copy(result_path, zip_path)

    elif product == "Vector":
        zip_path = result_path.split(".")[0]
        for vector_result_path in vector_result_paths:
            print("vector_result_path: ", vector_result_path)
            sub_zip_path = os.path.join(zip_path,
                                        os.path.basename(vector_result_path.split(".")[0]))
            os.makedirs(sub_zip_path)
            for af in all_files:
                ending = ".".join(af.split(".")[1:])
                target_path = os.path.join(sub_zip_path, os.path.basename(sub_zip_path) + "." + ending)
                print(f"copy {af} to {target_path}")
                shutil.copy(af, target_path)
            print(f"copy {vector_result_path} to {zip_path}")
            shutil.copy(vector_result_path, sub_zip_path)

    shutil.make_archive(zip_path, 'zip', zip_path)

    # XCOM Push ---------------------------------------------------------------
    context['ti'].xcom_push(key="result", value=zip_path+".zip")


dag = DAG(
    'get_product',
    default_args=default_args,
    description='Get-Product DAG',
    schedule_interval=None,
)

t1 = BashOperator(
    task_id='output_directory_creation',
    bash_command='mkdir /mnt/interim/{{ run_id }}; '
                 'chmod -R 777 /mnt/interim/{{ run_id }}',
    dag=dag,
)

t2 = PythonOperator(
    task_id='state',
    python_callable=state_function,
    provide_context=True,
    dag=dag,
)

#t3 = PythonOperator(
#    task_id='get_product',
#    python_callable=get_product,
#    provide_context=True,
#    dag=dag
#)

#t3 = BashOperator(
#    task_id='get_product',
#    bash_command='python3 /usr/lib/airflow/extra_code/get_product_extra.py -p {{ dag_run.conf["product"] }} -a "{{ dag_run.conf["aoi"] }}" -r {{ run_id }}',
#    xcom_push=True,
#    dag=dag,
#)

t3 = DockerOperator(
    task_id='get_product',
    image='imagehub.geoville.com/clcplus_get_product',
    command='python3 -u /main.py -p {{ dag_run.conf["product"] }} -a "{{ dag_run.conf["aoi"] }}" -r {{ run_id }}',
    volumes=["/home/geoville:/home/geoville",
             "/mnt/products:/mnt/products",
             "/mnt/interim:/mnt/interim"],
    network_mode="host",
    user="1002:1002",
    xcom_push=True,
    dag=dag,
)

t4 = PythonOperator(
    task_id='upload_result',
    python_callable=upload_result,
    provide_context=True,
    dag=dag,
)

t5 = BashOperator(
    task_id='remove_interim_data',
    bash_command='rm -r /mnt/interim/{{ run_id }}',
    dag=dag,
)
t6 = PythonOperator(
    task_id='get_product_success',
    python_callable=success,
    provide_context=True,
    dag=dag,
    retries=3,
)
t7 = PythonOperator(
    task_id='get_product_failure',
    python_callable=failure,
    trigger_rule='one_failed',
    provide_context=True,
    dag=dag,
    retries=3,
)

t1 >> t2 >> t3 >> t4 >> t5
t5 >> t6
t5 >> t7
