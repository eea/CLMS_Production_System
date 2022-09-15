# Standard library
import os
import unittest

# third party library
import numpy as np
import rasterio as rio
from affine import Affine
from rasterio.crs import CRS
from shapely.geometry.polygon import Polygon

# own functionality
from lib.storage_utils import write_raster_by_group
from geoville_storage_gate.raster import read_by_group, \
    read_by_bounds, update_by_bounds, get_dates


class StorageGateSystemRasterTests(unittest.TestCase):
    """
    System Test of the main storage gate raster functions
    """

    def test_write_read_raster_by_group(self):
        """
        Basic function to test the reading and writing of a raster
        without bounds
        """
        # test variables
        array = np.random.randint(10, size=(10, 20, 20))
        profile = {"width": 20, "height": 20, "nodata": 255, "dtype": 'uint8',
                   "transform": Affine(1, 1, 1, 1, 1, 1),
                   "crs": CRS.from_epsg(4326)}
        ncdf_path = "/tmp/testfile.nc"
        group = "test"
        start_time = "2019-05-01"
        end_time = "2019-05-10"
        array_variable = "raster"

        # write a test raster
        write_raster_by_group(array,
                              profile,
                              ncdf_path,
                              group,
                              start_time,
                              end_time,
                              array_variable=array_variable)

        # read the test raster
        written_array, written_profile = read_by_group(
                                               ncdf_path,
                                               start_time,
                                               end_time,
                                               group,
                                               array_variable=array_variable)

        # remove temporary test file
        os.remove(ncdf_path)

        # check if the read test raster equals the array used for writing it
        self.assertEqual(array.all(), written_array.all())

    def test_write_read_raster_subset(self):
        """
        Basic function to test the reading and writing of a raster with bounds
        """

        # test variables
        with rio.open("{}/tests/data/"
                      "test_raster.tif".format(os.getcwd())) as src:
            array = src.read()
            profile = src.profile

        ncdf_path = "/tmp/testfile.nc"
        group = "test"
        start_time = "2019-05-01"
        end_time = "2019-05-01"
        array_variable = "raster"

        bounds = Polygon([[661697.166128716, 4320223.863762978],
                          [660697.2823883237, 4320130.124662316],
                          [660603.5432876621, 4321296.655692774],
                          [661738.8279512323, 4321234.162958999],
                          [661697.166128716, 4320223.863762978]])

        # write a test raster
        write_raster_by_group(array,
                              profile,
                              ncdf_path,
                              group,
                              start_time,
                              end_time,
                              array_variable=array_variable)

        # read the test raster
        subset_array, subset_profile = read_by_bounds(
                                              ncdf_path,
                                              start_time,
                                              end_time,
                                              bounds,
                                              array_variable=array_variable)

        # remove temporary test file
        os.remove(ncdf_path)

        # check if the read test raster equals the array used for writing it
        with rio.open("{}/tests/data/"
                      "test_raster_subset.tif".format(os.getcwd())) as src:
            expected_array = src.read()
        self.assertEqual(expected_array.all(), subset_array.all())

    def test_update_raster_subset(self):
        """
        Test the update of an existing netcdf dataset
        """
        # test variables
        with rio.open("{}/tests/data/test_raster.tif".format(os.getcwd())) \
                as src:
            array = src.read()
            profile = src.profile

        ncdf_path = "/tmp/testfile.nc"
        group = "test"
        start_time = "2019-05-01"
        end_time = "2019-05-01"
        array_variable = "raster"

        # write a test raster
        write_raster_by_group(array,
                              profile,
                              ncdf_path,
                              group,
                              start_time,
                              end_time,
                              array_variable=array_variable)

        # update written raster
        update_for_subset = (array * 0) + 99
        bounds = Polygon([[661697.166128716, 4320223.863762978],
                          [660697.2823883237, 4320130.124662316],
                          [660603.5432876621, 4321296.655692774],
                          [661738.8279512323, 4321234.162958999],
                          [661697.166128716, 4320223.863762978]])

        update_by_bounds(update_for_subset,
                         profile,
                         ncdf_path,
                         bounds,
                         start_time,
                         end_time,
                         array_variable=array_variable)

        # read updated array
        updated_array, updated_profile = read_by_bounds(
                                              ncdf_path,
                                              start_time,
                                              end_time,
                                              bounds,
                                              array_variable=array_variable)

        # remove temporary netcdf file
        os.remove(ncdf_path)

        updated_array_without_nodata = updated_array[updated_array !=
                                                     profile["nodata"]]
        self.assertTrue(np.all(updated_array_without_nodata == 99))

    def test_get_dates(self):
        """
        Test getting the time dimension of an existing netcdf dataset
        """
        # test variables
        with rio.open("{}/tests/data/test_raster.tif".format(os.getcwd())) \
                as src:
            array = src.read()
            profile = src.profile

        ncdf_path = "/tmp/testfile.nc"
        group = "test"
        start_time = "2019-05-01"
        end_time = "2019-05-01"
        array_variable = "raster"

        # write a test raster
        write_raster_by_group(array,
                              profile,
                              ncdf_path,
                              group,
                              start_time,
                              end_time,
                              array_variable=array_variable)

        # get time dimension
        existing_dates = get_dates(ncdf_path, group)

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual(["2019-05-01"], existing_dates)

    # TODO: Test reading a raster with bounds that intersect several groups
