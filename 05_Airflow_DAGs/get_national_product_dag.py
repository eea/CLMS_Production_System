from datetime import timedelta
import os
import shutil
import boto3
import airflow
import pyproj
import shapely.wkt
from shapely.ops import transform
import xarray as xr
import geopandas as gpd
from affine import Affine
from shapely.geometry import mapping
import rioxarray as riox
from rioxarray.merge import merge_datasets
from airflow import DAG
from shapely import wkt
from pyproj import CRS
import subprocess as sp
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from geoville_ms_dag_state.dag_state import failed_dag, success_dag, \
    running_dag
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from lib.storage_utils import get_raster_group_names_intersecting_bounds, \
    read_netcdf
import dask_geopandas
from osgeo import gdal
from geoalchemy2.shape import to_shape


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
    'queue': 'get_national_product',
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


def failure(context):
    shutil.rmtree("/mnt/interim/{}".format(context['dag_run'].run_id),
                  ignore_errors=True)
    failed_dag(context['dag_run'].run_id)


def success(context):
    result = context['task_instance'].xcom_pull(key="result",
                                                task_ids='upload_result')
    success_dag(context['dag_run'].run_id, result)


def state_function(**context):
    running_dag(context['run_id'])


def upload_result(**context):
    aws = \
        boto3.resource('s3',
                       region_name="eu-central-1",
                       aws_access_key_id="bc8e686837c2476ba4dcef06ba7272ca",
                       aws_secret_access_key="2e7516dc941f4bdcae1204d51c354bee",
                       endpoint_url="https://cf2.cloudferro.com:8080")

    bucket = aws.Bucket("clcplus-public")
    product_file = context['task_instance'].xcom_pull(key="result",
                                                      task_ids='get_national_product')
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
    for idx, row in pu_gdf.iterrows():
        if bounds.intersects(row["geometry"]):
            if row["geometry"].within(bounds):
                pus_within_bounds.append(row["PU_ID"])
            else:
                pus_intersecting_bounds.append(row["PU_ID"])

    groups_of_netcdf = get_group_names(input_ncdf)
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
        intersection = gdf[gdf.intersects(bounds)]
        intersection['geometry'] = intersection.buffer(0)
        intersection = intersection.compute()
        intersection = gpd.clip(intersection, bounds)
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


def get_national_product(**context):

    product = context['dag_run'].conf['product']
    nation = context['dag_run'].conf['nation'].upper()

    sql = """SELECT
                dst_wkt,
                tr_wkt,
                ST_AsText(geometry)
             FROM
                national_products.national_product_information
             WHERE
                country = %s
    """
    dst_wkt, tr_wkt, geometry = read_from_database_one_row(sql,
                                                           (nation,),
                                                           os.getenv('DATABASE_CONFIG_FILE'),
                                                           os.getenv('DATABASE_CONFIG_FILE_SECTION'),
                                                           True)

    # buffer national boundary by 100km
    national_crs = CRS.from_wkt(dst_wkt)
    print("dst_wkt: ", dst_wkt)
    print("national_crs: ", national_crs)

    national_geometry = shapely.wkt.loads(geometry)

    reproject = pyproj.Transformer.from_crs(national_crs,
                                           pyproj.CRS('EPSG:3035'),
                                           always_xy=True).transform
    geometry = transform(reproject, national_geometry)
    bounds = geometry.buffer(100000)

    ncdf_output_path = f"/mnt/products/{product}.nc"

    # retrieve data from netcdf -----------------------------------------------
    result_path = None

    if product == "Raster":
        result_path = \
            os.path.join("/mnt/interim", context['dag_run'].run_id,
                         f"{product}_{nation}_{context['dag_run'].run_id}.tif")

        cropped_ds = read_raster_by_bounds(ncdf_output_path, bounds)
        cropped_ds.raster.rio.to_raster(result_path, compress='LZW')

    if product == "Vector":
        result_path = \
            os.path.join("/mnt/interim", context['dag_run'].run_id,
                         f"{product}_{nation}_{context['dag_run'].run_id}.gpkg")

        vector_result_paths = \
            read_vector_by_bounds(ncdf_output_path, national_geometry, result_path)
        print("vector_result_paths: ", vector_result_paths)

    # Reproject to national projection and finally clip to national boundary --
    if product == "Raster":

        # reproject
        tmp_path = result_path.replace(".tif", "_tmp.tif")
        # cmd = f"gdalwarp -t_srs '{dst_wkt}' -ct '{tr_wkt}' -tr 10 10 -tap -of GTiff -overwrite {result_path} {tmp_path}"
        # print(cmd)
        # process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        # _, err = process.communicate()
        # if process.returncode != 0:
        #     raise Exception('CMD ({}) failed with: {}'.format(cmd, str(err)))
        gdal.Warp(tmp_path,  # path of destination file
                  result_path,  # path of source file
                  format="GTiff",  # destination format
                  creationOptions=["COMPRESS=LZW", "NUM_THREADS=6"],
                  # optional creation options for used format
                  dstSRS=national_crs,
                  # wkt string of destination CRS from .CSV table. Must match destination CRS defined in coordinate operation!!
                  coordinateOperation=tr_wkt,
                  # wkt transformation string from .CSV table
                  xRes=10,
                  # output X resolution (necessary for targetAlignedPixels option)
                  yRes=10,
                  # output Y resolution (necessary for targetAlignedPixels option)
                  targetAlignedPixels=True,
                  # aligns the coordinates of the extent of the output file to the values of xRes, yRes. Important for clipping operations.
                  multithread=True)

        # clip
        xds = riox.open_rasterio(tmp_path)
        xds_clipped = xds.rio.clip(gpd.GeoDataFrame(geometry=[national_geometry],
                             crs=national_crs).geometry.apply(mapping),
            national_crs)

        # overwrite result_path with xds_reprojected_clipped
        xds_clipped.rio.to_raster(result_path)

    if product == "Vector":
        reprojected_vector_paths = []
        for vector_result_path in vector_result_paths:
            print("vector_result_path: ", vector_result_path)
            tmp_path = vector_result_path.replace(".gpkg", "_natProj.gpkg")
            gdal.VectorTranslate(tmp_path,
                                 # path of destination file
                                 vector_result_path,  # path of input file
                                 format="GPKG",  # output format
                                 dstSRS=dst_wkt,
                                 # wkt string of destination CRS from .CSV table. Must match destination CRS defined in coordinate operation!!
                                 coordinateOperation=tr_wkt,
                                 # wkt transformation string from .CSV table
                                 reproject=True)  # needs to be set to true
            reprojected_vector_paths.append(tmp_path)

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
        for reprojected_vector_path in reprojected_vector_paths:
            print("reprojected_vector_path: ", reprojected_vector_path)
            sub_zip_path = os.path.join(zip_path,
                                        os.path.basename(reprojected_vector_path.split(".")[0]))
            os.makedirs(sub_zip_path)
            for af in all_files:
                ending = ".".join(af.split(".")[1:])
                target_path = os.path.join(sub_zip_path, os.path.basename(sub_zip_path) + "." + ending)
                print(f"copy {af} to {target_path}")
                shutil.copy(af, target_path)
            print(f"copy {reprojected_vector_path} to {zip_path}")
            shutil.copy(reprojected_vector_path, sub_zip_path)

    shutil.make_archive(zip_path, 'zip', zip_path)

    # XCOM Push ---------------------------------------------------------------
    context['ti'].xcom_push(key="result", value=zip_path+".zip")


dag = DAG(
    'get_national_product',
    default_args=default_args,
    description='Get-Product DAG',
    schedule_interval=None,
    on_failure_callback=failure,
    on_success_callback=success
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

t3 = PythonOperator(
    task_id='get_national_product',
    python_callable=get_national_product,
    provide_context=True,
    dag=dag
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

t1 >> t2 >> t3 >> t4 >> t5
