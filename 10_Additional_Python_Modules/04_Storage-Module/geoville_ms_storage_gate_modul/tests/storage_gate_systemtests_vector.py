import os
import unittest

import geopandas as gpd
from shapely.geometry.polygon import Polygon

from geoville_storage_gate.vector import read_by_group, \
                                         read_by_bounds, upsert_by_bounds, \
                                         read_by_attribute, create_by_group, \
                                         update_by_attribute, crop_to_bounds


class StorageGateSystemVectorTests(unittest.TestCase):
    """
    System Test of the main storage gate vector functions
    """

    def test_write_read_vector_by_group(self):
        """
        Basic function to test the reading and writing of a vector
        without bounds
        """
        # test variables
        example_vector = '{}/tests/data/test_vector.shp'.format(os.getcwd())
        example_geodataframe = gpd.read_file(example_vector)
        ncdf_path = "/tmp/testfile.nc"
        group = "test_vector_group"

        # write a test vector
        create_by_group(example_geodataframe, ncdf_path, group,
                        attributes={"crs": example_geodataframe.crs})

        # read the test vector
        written_geodataframe = read_by_group(ncdf_path, group)

        # remove temporary test file
        os.remove(ncdf_path)

        # check if the read test vector equals the geodataframe used for
        # writing it
        self.assertTrue(written_geodataframe.equals(example_geodataframe))

    def test_write_read_vector_by_bounds(self):
        """
        Basic function to test the reading and writing of a vector
        with bounds
        """
        # test variables
        example_vector = '{}/tests/data/test_vector.shp'.format(os.getcwd())
        example_geodataframe = gpd.read_file(example_vector)
        ncdf_path = "/tmp/testfile.nc"
        group = "test_vector_group"

        # write a test vector
        create_by_group(example_geodataframe, ncdf_path, group,
                        attributes={"crs": example_geodataframe.crs})

        # update the test vector
        update_vector = "{}/tests/data/" \
                        "test_update_vector.shp".format(os.getcwd())
        update_geodataframe = gpd.read_file(update_vector)
        bounds = Polygon([[171294, 509586],
                          [408599, 513476],
                          [308101, 224301],
                          [132392, 336470]])
        upsert_by_bounds(update_geodataframe, ncdf_path, bounds, "intersects")

        # read the test vector
        written_geodataframe = read_by_bounds(ncdf_path, bounds,
                                              relation_to_bounds="intersects")

        # reset the index for comparison
        written_geodataframe = written_geodataframe.reset_index(drop=True)

        # remove temporary test file
        os.remove(ncdf_path)

        # check if the read test vector equals the geodataframe used for
        # writing it
        expected_geodataframe = \
            gpd.read_file("{}/tests/data/"
                          "test_expected_update_vector.shp".format(
                                                                  os.getcwd()))
        self.assertTrue(written_geodataframe["TileID"].
                        equals(expected_geodataframe["TileID"]))

    def test_write_read_vector_by_attribute(self):
        """
        Basic function to test the reading and writing of a vector
        attribute
        """
        # test variables
        example_vector = '{}/tests/data/test_vector.shp'.format(os.getcwd())
        example_geodataframe = gpd.read_file(example_vector)
        ncdf_path = "/tmp/testfile.nc"
        group = "test_vector_group"

        # write a test vector
        create_by_group(example_geodataframe, ncdf_path, group,
                        attributes={"crs": example_geodataframe.crs})

        # update all vector features where the attribute "left" is 98900
        # with 999
        update_by_attribute(ncdf_path, "left", 98900, "left", 999, query='=')

        # read all vector features where the attribute "left" is 999
        written_geodataframe = read_by_attribute(ncdf_path, "left", 999,
                                                 query='=')

        # remove temporary test file
        os.remove(ncdf_path)

        self.assertTrue(
            written_geodataframe["TileID"].
            equals(example_geodataframe[example_geodataframe["left"]
                                        == 98900]["TileID"]))

    def test_crop_to_bounds(self):
        """
        Basic function to test the crop_to_bounds function
        """
        # test variables
        example_vector = '{}/tests/data/test_vector.shp'.format(os.getcwd())
        example_geodataframe = gpd.read_file(example_vector)
        bounds = Polygon([[171294, 509586],
                          [408599, 513476],
                          [308101, 224301],
                          [132392, 336470]])
        written_geodataframe = crop_to_bounds(example_geodataframe, bounds)

        self.assertTrue(13, len(written_geodataframe["TileID"]))
