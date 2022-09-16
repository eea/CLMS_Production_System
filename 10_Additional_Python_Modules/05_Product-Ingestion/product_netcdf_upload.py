"""
Before this script can run on the machine where the netcdf products are
provided, the respective data needs to be uploaded on the machine.
Then this script will create or append the data to the existing product netcdf
file.

"""

# standard modules
import os
import argparse
import subprocess as sp
from warnings import warn

# third party modules
import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
import dask.array as da
import dask.dataframe as dd

# in-house modules
from lib.storage_utils import get_group, write_netcdf
from geoville_storage_gate.netCDF import get_group_names
from geoville_storage_gate.raster import create_by_group as rcg
from geoville_storage_gate.raster import upsert_by_group as rug
from geoville_storage_gate.vector import create_by_group as vcg
from geoville_storage_gate.vector import upsert_by_group as vug


def vug_csv(ncdf_path, group, csv_file):

    ncdf_dataset = write_netcdf(ncdf_path)
    ncdf_group = get_group(ncdf_dataset, group)
    df = ncdf_group.variables

    csv_df = dd.read_csv(csv_file, delimiter=";")
    csv_df = csv_df.sort_values('id')

    # get id and compare if both are sorted
    df_id = pd.DataFrame(df["ID"][:].data, columns=["ID"])

    if not da.all(df_id["ID"] == csv_df["id"].compute()).compute():
        raise Exception("index (id) of netcdf file and new csv do not align")

    for c in csv_df.columns:
        if c not in df:
            print(c, " attribute gets appended")
            ncdf_variable = ncdf_group.createVariable(c,
                                                      csv_df[c].dtype,
                                                      ("features",))
            ncdf_variable[:] = np.array(csv_df[c])

    ncdf_dataset.close()


# PARSER ======================================================================
parser = argparse.ArgumentParser(description="This script converts CLC+ "
                                             "Backbone products to netCDF "
                                             "files.")
parser.add_argument("-n", "--Name", type=str, metavar="", required=True,
                    help="Product Name")
parser.add_argument("-u", "--Unit", type=str, metavar="", required=True,
                    help="Unit for netCDF grouping (can be PU or SPU, "
                         "but uniform across product)")
parser.add_argument("-i", "--Input", type=str, metavar="", required=True,
                    help="Path to the input raster (GeoTiff), "
                         "input vector (Geopackage) or input vector attribute "
                         "(csv)")
parser.add_argument("-o", "--Output", type=str, metavar="", required=False,
                    default=None, help="Not required, only for debugging! "
                                       "Path to the output netcdf file.")

args = parser.parse_args()


if __name__ == "__main__":

    product = args.Name
    unit = args.Unit
    ncdf_output_path = args.Output

    # RASTER ==================================================================
    if product == "Raster" \
            or product == "Confidence" \
            or product == "DataScore":

        if not ncdf_output_path:
            ncdf_output_path = f"/mnt/products/{product}.nc"

        pu_file = args.Input

        # assign nodata value
        cmd = f"gdal_edit.py -a_nodata 255 {pu_file}"
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        out, err = p.communicate()
        if p.returncode != 0:
            raise Exception(f"gdal_edit failed with: {err}")

        # read file
        with rio.open(pu_file) as src:
            array = src.read()
            profile = src.profile

        # create or append to netcdf
        if not os.path.exists(ncdf_output_path):
            rcg(array, profile, ncdf_output_path, unit, "2018-01-01",
                "2018-01-01", array_variable="raster")
        else:
            rug(array, profile, ncdf_output_path, unit, "2018-01-01",
                "2018-01-01", array_variable="raster")

    # VECTOR ==================================================================
    elif product == "Vector" or product == "VectorAttribution":

        if not ncdf_output_path:
            ncdf_output_path = f"/mnt/products/Vector.nc"

        pu_file = args.Input

        # create or append to netcdf
        if not os.path.exists(ncdf_output_path):
            # netcdf product file does not exist yet
            if not pu_file.endswith(".gpkg"):
                raise Exception("If the netcdf product file does not exists, "
                                "the first file needs to be a Geopackage to "
                                "insert the geometries.")

            gdf = gpd.read_file(pu_file)
            vcg(gdf, ncdf_output_path, unit, {"crs": gdf.crs})

        else:
            # netcdf product file exists
            groups = get_group_names(ncdf_output_path)
            if unit not in groups:
                # netcdf group does not exist
                if not pu_file.endswith(".gpkg"):
                    raise Exception(
                        "If the unit does not exist within the netcdf "
                        "product file, the first file needs to be a Geopackage"
                        " to insert the geometries.")
                gdf = gpd.read_file(pu_file)
                vcg(gdf, ncdf_output_path, unit, {"crs": gdf.crs})
            else:
                # netcdf group exists
                if pu_file.endswith(".csv") and product == "VectorAttribution":
                    # input crs (new attribute)
                    vug_csv(ncdf_output_path, unit, pu_file)
                elif pu_file.endswith(".gpkg") and product == "Vector":
                    # input gpkg (new geometries)
                    warn(f"The group {unit} already exists. If you want to"
                         f" update geometries, please ensure that the input "
                         f"Geopackage has a reasobale size. "
                         f"If too many geometries are included because they "
                         f"need to be changed, this task can take forever.",
                         ResourceWarning)
                    gdf = gpd.read_file(pu_file)
                    vug(gdf, ncdf_output_path, unit, {"crs": gdf.crs})
                else:
                    raise Exception("The netdf product and the group do exist."
                                    " Please provide a Geopackage when "
                                    "inserting data for the VectorAttribution-"
                                    " or a CSV file for the Vector-product.")

    else:
        raise Exception(f"Product {product} does not exist. Please choose "
                        f"from 'Raster', 'Confidence', 'DataScore', 'Vector' "
                        f"or 'VectorAttribution'")
