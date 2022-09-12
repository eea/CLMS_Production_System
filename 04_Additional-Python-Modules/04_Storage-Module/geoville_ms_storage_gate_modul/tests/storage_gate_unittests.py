# Standard library
import os
import tempfile
import unittest

# third party library
import numpy as np
import rasterio as rio
import geopandas as gpd
from shapely.geometry.polygon import Polygon

# own functionality
from geoville_storage_gate.netCDF import get_group_names
from lib.storage_utils import write_netcdf, read_netcdf, set_group, \
    get_group, get_list_of_datestrings, set_temporal_bounds, \
    get_temporal_bounds, create_dimensions, set_variable_subset, \
    get_variable_subset, get_raster_group_names_intersecting_bounds, \
    get_group_bbox, get_vector_group_names_intersecting_bounds, \
    check_attribute_consistency, check_variable_consistency, \
    write_raster_by_group


class StorageGateUnitTests(unittest.TestCase):
    """
    Unit Test of the storage utils functions
    """

    def test_write_ncdf_with_wrong_path(self):
        """
        Test the writing of a netcdf file with a wrong path suffix
        """
        # create temporary netcdf file
        _, ncdf_path = tempfile.mkstemp()

        # write with the wrong path
        failed = False
        try:
            write_netcdf(ncdf_path)
        except ValueError:
            failed = True

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_write_ncdf_correctly(self):
        """
        Test the writing of a netcdf file
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"

        # read with the correct path
        failed = False
        try:
            write_netcdf(ncdf_path)
        except ValueError:
            failed = True

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_read_ncdf_with_wrong_path(self):
        """
        Test the reading of a netcdf file with a wrong path suffix
        """
        # create temporary netcdf file
        _, ncdf_path = tempfile.mkstemp()

        # read with the wrong path
        failed = False
        try:
            read_netcdf(ncdf_path)
        except ValueError:
            failed = True

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_read_ncdf_with_nonexisting_path(self):
        """
        Test the reading of a netcdf file with a nonexisting path
        """
        # nonexisting path
        ncdf_path = "/tmp/jxhfdksdghljkshglskurhg.nc"

        # read with the wrong path
        self.assertRaises(IOError, read_netcdf, ncdf_path)

    def test_read_ncdf_without_content(self):
        """
        Test the reading of a file ending with .nc
        but not being a netcdf file with its structure
        """
        # create temporary file ending with the suffix .nc
        _, ncdf_path = tempfile.mkstemp(".nc")

        # read with a correct path to a wrong file
        failed = False
        try:
            read_netcdf(ncdf_path)
        except OSError:
            failed = True

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_read_ncdf_correctly(self):
        """
        Test the reading of a netcdf file
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        write_netcdf(ncdf_path)

        # read with the correct path
        failed = False
        try:
            read_netcdf(ncdf_path)
        except ValueError or IOError:
            failed = True

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_set_nonexisting_group(self):
        """
        Test the set_group function with a nonexisting group.
        The function should create that group.
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # set the nonexisting netcdf group
        set_group(ncdf_dataset, "test_group_name")

        # check if group exists now
        success = False
        if "test_group_name" in ncdf_dataset.groups:
            success = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(success)

    def test_set_group_without_groupname(self):
        """
        Test the set_group function without defining a group
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # fail setting None as a group name
        failed = False
        try:
            set_group(ncdf_dataset, None)
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_nonexisting_group(self):
        """
        Test the get_group function with a nonexisting group.
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # fail by getting the nonexisting netcdf group
        failed = False
        try:
            get_group(ncdf_dataset, "test_group_name")
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_group_without_groupname(self):
        """
        Test the get_group function without defining a group
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # get the netcdf dataset because the group is not defined (None)
        failed = False
        try:
            get_group(ncdf_dataset, None)
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_get_existing_group(self):
        """
        Test the get_group function with a defined group
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_name")

        # get the netcdf group
        failed = False
        try:
            get_group(ncdf_dataset, "test_group_name")
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_get_list_of_datestrings_with_wrong_format(self):
        """
        Test the get_list_of_datestrings function
        with a wrong data string format
        """
        # date examples
        start_date = "20190501"
        end_date = "20190530"

        # get a list of datestrings
        self.assertRaises(ValueError, get_list_of_datestrings, start_date,
                          end_date)

    def test_get_list_of_datestrings_with_start_time_after_end_time(self):
        """
        Test the get_list_of_datestrings function
        with a start date that is later than the end date
        """
        # date examples
        start_date = "2019-05-30"
        end_date = "2019-05-01"

        # get a list of datestrings
        self.assertRaises(ValueError, get_list_of_datestrings, start_date,
                          end_date)

    def test_get_list_of_datestrings_with_correct_input(self):
        """
        Test the get_list_of_datestrings function with correct input
        """
        # date examples
        start_date = "2019-05-29"
        end_date = "2019-06-02"

        # expected outcome
        datestrings = ["2019-05-29", "2019-05-30", "2019-05-31", "2019-06-01",
                       "2019-06-02"]

        # get a list of datestrings
        self.assertEqual(datestrings,
                         get_list_of_datestrings(start_date, end_date))

    def test_set_temporal_bounds(self):
        """
        Test the set_temporal_bounds function with correct input
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_name")
        ncdf_group = get_group(ncdf_dataset, "test_group_name")

        # set temporal bounds
        set_temporal_bounds(ncdf_group, "2019-05-29", "2019-06-02")

        # expected result
        expected_time_variable = np.array(["2019-05-29", "2019-05-30",
                                           "2019-05-31", "2019-06-01",
                                           "2019-06-02"])

        # check if expected result equals the result completely
        complete_array_equal = np.all(expected_time_variable
                                      == ncdf_group.variables["time"][:])

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(complete_array_equal)

    def test_get_temporal_bounds_without_time_variable_in_group(self):
        """
        Test the get_temporal_bounds function with incorrect input
        The netcdf group is empty and has no 'time' variable.
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_name")
        ncdf_group = get_group(ncdf_dataset, "test_group_name")

        # date examples
        start_date = "2019-05-29"
        end_date = "2019-06-02"

        # get temporal bounds
        failed = False
        try:
            get_temporal_bounds(ncdf_group, start_date, end_date)
        except KeyError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_temporal_bounds_of_missing_timestep(self):
        """
        Test the get_temporal_bounds function with incorrect input
        The netcdf group has times between 2019-05-29 and 2019-06-02
        but the request starts earlier (2019-05-20) and ends later (2019-06-10)
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_name")
        ncdf_group = get_group(ncdf_dataset, "test_group_name")
        set_temporal_bounds(ncdf_group, "2019-05-29", "2019-06-02")

        # date examples
        start_date = "2019-05-20"
        end_date = "2019-06-10"

        # get temporal bounds
        failed = False
        try:
            get_temporal_bounds(ncdf_group, start_date, end_date)
        except KeyError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_temporal_bounds_with_time_variable_in_group(self):
        """
        Test the get_temporal_bounds function with correct input
        The netcdf group already has data included
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        write_raster_by_group(np.random.randint(10, size=(30, 20, 20)),
                              {"nodata": 255,
                               "dtype": "uint8",
                               "transform": np.array([10, 0, 12345,
                                                      0, 10, 12345,
                                                      0, 0, 0]),
                              "crs": "test-crs-placeholder"},
                              ncdf_path,
                              "test_group_name",
                              "2019-05-01",
                              "2019-05-30",
                              array_variable="raster")

        # read that temporary netcdf file
        ncdf_dataset = read_netcdf(ncdf_path)
        ncdf_group = get_group(ncdf_dataset, "test_group_name")

        # date examples
        start_date = "2019-05-04"
        end_date = "2019-05-18"

        # get temporal bounds
        temporal_bounds = get_temporal_bounds(ncdf_group, start_date, end_date)

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual((3, 18), temporal_bounds)

    def test_create_dimensions(self):
        """
        Test the create_dimensions function
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_name")
        ncdf_group = get_group(ncdf_dataset, "test_group_name")

        # test dimensions
        dimensions = {"x": 10, "y": 30, "time": 0, "test": 999}

        # create dimensions
        create_dimensions(dimensions, ncdf_group)

        # save the resulted dimensions in a checkable format
        result = dict(zip(ncdf_group.dimensions.keys(),
                          [v.size for v in ncdf_group.dimensions.values()]))

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual(dimensions, result)

    def test_set_variable_subset_for_empty_dataset(self):
        """
        Test the set_variable_subset function without bounds and attributes
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_temporal_bounds(ncdf_dataset, "2019-05-29", "2019-06-02")

        # test array
        array = np.random.randint(255, size=(5, 100, 100))

        # update the raster within the bounds with the array
        set_variable_subset(ncdf_dataset, "raster", 0, 5,
                            None, array, attributes={"nodata": 255})

        # read that temporary netcdf file
        outcome = read_netcdf(ncdf_path).variables["raster"][:]

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(np.all(array == outcome))

    def test_set_variable_subset_with_bounds_without_attributes(self):
        """
        Test the set_variable_subset function with bounds but
        without the required attributes
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_temporal_bounds(ncdf_dataset, "2019-05-29", "2019-06-02")

        # test array and bounds
        array = np.random.randint(255, size=(5, 100, 100))
        bounds = Polygon([[1, 0], [0, 1], [0, 0], [1, 1]])

        # update the raster within the bounds with the array
        failed = False
        try:
            set_variable_subset(ncdf_dataset, "raster", 0, 5,
                                bounds, array, attributes=None)
        except AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_set_variable_subset_out_of_bounds(self):
        """
        Test the set_variable_subset function with bounds but
        they are outside the array
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_temporal_bounds(ncdf_dataset, "2019-05-29", "2019-06-02")

        # test array and bounds
        array = np.random.randint(255, size=(5, 100, 100))
        bounds = Polygon([[1, 0], [0, 1], [0, 0], [1, 1]])
        attributes = {"nodata": 255, "transform": np.array([10, 0, 12345,
                                                            0, 10, 12345,
                                                            0, 0, 0])}

        # update the raster within the bounds with the array
        failed = False
        try:
            set_variable_subset(ncdf_dataset, "raster", 0, 5,
                                bounds, array, attributes=attributes)
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_variable_subset_without_existing_variable(self):
        """
        Test the get_variable_subset function without an existing variable
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # try to get the "raster" variable although it does not exist
        failed = False
        try:
            get_variable_subset(ncdf_dataset, "raster", 0, 5, None)
        except KeyError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_variable_subset_with_bounds_without_attributes(self):
        """
        Test the get_variable_subset function with bounds but
        without the required attributes
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        dimensions = {"x": 100, "y": 100, "time": None}
        create_dimensions(dimensions, ncdf_dataset)
        ncdf_dataset.createVariable("raster", np.int, ("time", "y", "x"))

        # test bounds
        bounds = Polygon([[1, 0], [0, 1], [0, 0], [1, 1]])

        # update the raster within the bounds with the array
        failed = False
        try:
            get_variable_subset(ncdf_dataset, "raster", 0, 5, bounds)
        except AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_variable_subset_out_of_bounds(self):
        """
        Test the get_variable_subset function with bounds but
        hey are outside the array
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_temporal_bounds(ncdf_dataset, "2019-05-29", "2019-06-02")

        # test array and attributes
        array = np.random.randint(255, size=(5, 100, 100))
        attributes = {"nodata": 255, "transform": np.array([10, 0, 12345,
                                                            0, 10, 12345,
                                                            0, 0, 0])}

        # create the raster variable with the array
        set_variable_subset(ncdf_dataset, "raster", 0, 5,
                            None, array, attributes=attributes)

        # test bounds
        bounds = Polygon([[1, 0], [0, 1], [0, 0], [1, 1]])

        # update the raster within the bounds with the array
        failed = False
        try:
            get_variable_subset(ncdf_dataset, "raster", 0, 5,
                                bounds)
        except ValueError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_get_variable_subset_without_bounds(self):
        """
        Test the get_variable_subset function without bounds
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_temporal_bounds(ncdf_dataset, "2019-05-29", "2019-06-02")

        # test array and attributes
        array = np.random.randint(255, size=(5, 100, 100))
        attributes = {"nodata": 255, "transform": np.array([10, 0, 12345,
                                                            0, 10, 12345,
                                                            0, 0, 0])}

        # create the raster variable with the array
        set_variable_subset(ncdf_dataset, "raster", 0, 5,
                            None, array, attributes=attributes)

        # get the array
        failed = False
        try:
            get_variable_subset(ncdf_dataset, "raster", 0, 5, None)
        except ValueError or KeyError or AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_get_raster_group_names_intersecting_bounds(self):
        """
        Test getting the names of all netcdf dataset groups that intersect the
        given bounds
        """
        # create temporary netcdf file
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)

        # configure temporary netcdf dataset
        set_group(ncdf_dataset, "test_group_name")
        ncdf_group = get_group(ncdf_dataset, "test_group_name")
        with rio.open("{}/tests/data/"
                      "test_raster.tif".format(os.getcwd())) as src:
            x = src.width
            y = src.height
            time = src.count
            ncdf_group.transform = np.array(src.transform)
        create_dimensions({"x": x, "y": y, "time": time}, ncdf_group)

        # intersect test bounds with groups
        bounds = Polygon([[660957.6687790505, 4321541.418900057],
                          [662999.0980823511, 4321708.066190122],
                          [662790.7889697695, 4319333.34230669],
                          [660916.0069565341, 4319416.665951723],
                          [660957.6687790505, 4321541.418900057]])

        intersection = get_raster_group_names_intersecting_bounds(ncdf_dataset,
                                                                  bounds)

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual(['test_group_name'], intersection)

    def test_get_group_names(self):
        """
        Test the get_groups function
        """
        # create temporary netcdf file with example groups
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_1")
        set_group(ncdf_dataset, "test_group_2")

        # close the dataset
        ncdf_dataset.close()

        # get groups
        ncdf_group_names = get_group_names(ncdf_path)

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual(["test_group_1", "test_group_2"], ncdf_group_names)

    def test_get_group_bbox(self):
        """
        Test the get_group_bbox function
        """
        # create temporary netcdf file with an example group
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group")

        # get the test group
        ncdf_group = get_group(ncdf_dataset, "test_group")

        # create dimensions
        dimensions = {"features": None,
                      "characteristics": 1}
        create_dimensions(dimensions, ncdf_group)

        # create a geometry variable
        ncdf_variable = ncdf_group.createVariable("geometry",
                                                  str, ("features",))

        # fill the geometry variable of the temporary netcdf file
        # with the test geodataframe's geometry
        test_geodataframe = gpd.read_file(
            "{}/tests/data/test_vector.shp".format(os.getcwd()))
        ncdf_variable[:] = np.array(
            test_geodataframe.geometry.apply(lambda g: g.wkt))

        # get the bbox of the group
        bbox = get_group_bbox(ncdf_dataset, "test_group")

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual('POLYGON ((98900 187300, 98900 637300, 458900 637300,'
                         ' 458900 187300, 98900 187300))', str(bbox))

    def test_get_vector_group_names_intersecting_bounds(self):
        """
        Test the get_vector_group_names_intersecting_bounds function
        """
        # create temporary netcdf file with an example group
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group")

        # get the test group
        ncdf_group = get_group(ncdf_dataset, "test_group")

        # create dimensions
        dimensions = {"features": None,
                      "characteristics": 1}
        create_dimensions(dimensions, ncdf_group)

        # create a geometry variable
        ncdf_variable = ncdf_group.createVariable("geometry",
                                                  str, ("features",))

        # fill the geometry variable of the temporary netcdf file
        # with the test geodataframe's geometry
        test_geodataframe = gpd.read_file(
            "{}/tests/data/test_vector.shp".format(os.getcwd()))
        ncdf_variable[:] = np.array(
            test_geodataframe.geometry.apply(lambda g: g.wkt))

        # check what groups intersect the test bounds
        bounds = Polygon([[98900, 187300],
                          [98900, 637300],
                          [458900, 637300],
                          [458900, 187300],
                          [98900, 187300]])
        intersecting_groups = get_vector_group_names_intersecting_bounds(
            ncdf_dataset, bounds)

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertEqual(["test_group"], intersecting_groups)

    def test_check_attribute_consistency_error(self):
        """
        Test the check_attribute_consistency function
        """
        # create temporary netcdf file with example groups
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_1")
        set_group(ncdf_dataset, "test_group_2")

        # get the temporary groups
        ncdf_group_1 = get_group(ncdf_dataset, "test_group_1")
        ncdf_group_2 = get_group(ncdf_dataset, "test_group_2")

        # set attributes
        ncdf_group_1.nodata = 255
        ncdf_group_2.nodata = 0.
        ncdf_group_1.dtype = np.int
        ncdf_group_2.dtype = np.float
        ncdf_group_1.crs = 32622
        ncdf_group_2.crs = 32622

        failed = False
        try:
            check_attribute_consistency(ncdf_dataset, ["test_group_1",
                                                       "test_group_2"])
        except AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertTrue(failed)

    def test_check_attribute_consistency_correct(self):
        """
        Test the check_attribute_consistency function
        """
        # create temporary netcdf file with example groups
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_1")
        set_group(ncdf_dataset, "test_group_2")

        # get the temporary groups
        ncdf_group_1 = get_group(ncdf_dataset, "test_group_1")
        ncdf_group_2 = get_group(ncdf_dataset, "test_group_2")

        # set attributes
        ncdf_group_1.nodata = 255
        ncdf_group_2.nodata = 255
        ncdf_group_1.key = rio.uint8
        ncdf_group_1.renameAttribute("key", "dtype")
        ncdf_group_2.key = rio.uint8
        ncdf_group_2.renameAttribute("key", "dtype")
        ncdf_group_1.crs = 32622
        ncdf_group_2.crs = 32622

        failed = False
        try:
            check_attribute_consistency(ncdf_dataset, ["test_group_1",
                                                       "test_group_2"])
        except AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_check_variable_consistency_correct(self):
        """
        Test the check_variable_consistency function
        """
        # create temporary netcdf file with example groups
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_1")
        set_group(ncdf_dataset, "test_group_2")

        # get the temporary groups
        ncdf_group_1 = get_group(ncdf_dataset, "test_group_1")
        ncdf_group_2 = get_group(ncdf_dataset, "test_group_2")

        # create dimensions
        dimensions = {"features": None,
                      "characteristics": 3}
        create_dimensions(dimensions, ncdf_group_1)
        create_dimensions(dimensions, ncdf_group_2)

        # create variables
        for ncdf_group in [ncdf_group_1, ncdf_group_2]:
            for test_variable in range(3):
                ncdf_group.createVariable("test_variable_"
                                          "{}".format(test_variable),
                                          str, ("features",))

        failed = False
        try:
            check_variable_consistency(ncdf_dataset, ["test_group_1",
                                                      "test_group_2"])
        except AttributeError:
            failed = True

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(failed)

    def test_check_variable_consistency_error(self):
        """
        Test the check_variable_consistency function
        """
        # create temporary netcdf file with example groups
        ncdf_path = "/tmp/testfile.nc"
        ncdf_dataset = write_netcdf(ncdf_path)
        set_group(ncdf_dataset, "test_group_1")
        set_group(ncdf_dataset, "test_group_2")

        # get the temporary groups
        ncdf_group_1 = get_group(ncdf_dataset, "test_group_1")
        ncdf_group_2 = get_group(ncdf_dataset, "test_group_2")

        # create dimensions
        dimensions = {"features": None,
                      "characteristics": 3}
        create_dimensions(dimensions, ncdf_group_1)
        create_dimensions(dimensions, ncdf_group_2)

        # create only one variables in group1 and three variables in group2
        ncdf_group_1.createVariable("test_variable_1", str, ("features",))
        for test_variable in range(3):
            ncdf_group_2.createVariable("test_variable_"
                                        "{}".format(test_variable),
                                        str, ("features",))

        consistency, all_variable_names = \
            check_variable_consistency(ncdf_dataset, ["test_group_1",
                                                      "test_group_2"])

        # close the dataset
        ncdf_dataset.close()

        # remove temporary netcdf file
        os.remove(ncdf_path)

        self.assertFalse(consistency)
