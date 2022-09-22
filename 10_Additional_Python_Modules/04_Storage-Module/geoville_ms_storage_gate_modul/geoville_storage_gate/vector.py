import os
import json
import operator
import numpy as np
import pandas as pd
from pyproj import CRS
from shapely import wkt
import geopandas as gpd
from warnings import warn
from shapely.geometry.polygon import Polygon

from lib.storage_utils import read_netcdf, write_netcdf, get_group, set_group,\
    check_variable_consistency, create_dimensions, get_group_bbox, \
    get_vector_group_names_intersecting_bounds


def crop_to_bounds(geodataframe, bounds):
    """
    Crops a geodataframe to the given polygon bounds

    :param geodataframe: Geodataframe
    :param bounds: boundary (shapely.geometry.polygon.Polygon)
    :return: Geodataframe cut to the given bounds
    """

    if not bounds.is_valid:
        raise ValueError("Invalid boundary")

    bounds_as_geodataframe = gpd.GeoDataFrame(index=[1], geometry=[bounds])
    geodataframe_cut_to_bounds = gpd.overlay(bounds_as_geodataframe,
                                             geodataframe,
                                             how="intersection")
    return geodataframe_cut_to_bounds


def read_by_group(ncdf_path, group, characteristics=None):
    """
    Reads a vector (subset) within the given netcdf file. The group and the
     characteristics define the file-intern data structure.

    :param ncdf_path: path to a netcdf file
    :param group: netcdf group name
    :param characteristics: list of desired column names / vector attributes
    :return: vector subset in form of a geodataframe
    """

    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get the specific group
    ncdf_group = get_group(ncdf_dataset, group)

    # get all characteristic/columns if not given
    if characteristics is None:
        characteristics = list(ncdf_group.variables.keys())

    # create empty dataframe
    output_dataframe = pd.DataFrame(columns=characteristics)

    # fill the output dataframe with the read group variables (characters)
    for character in characteristics:
        output_dataframe[character] = ncdf_group.variables[character][:]

    # convert pandas dataframe with wkt to geodataframe
    output_dataframe.geometry = output_dataframe.geometry.apply(wkt.loads)
    output_geodataframe = gpd.GeoDataFrame(output_dataframe,
                                           geometry="geometry")

    # define the crs of the geodataframe
    output_geodataframe.crs = CRS(ncdf_group.crs)

    # close the dataset
    ncdf_dataset.close()

    return output_geodataframe[~output_geodataframe.is_empty]


def read_by_bounds(ncdf_path, bounds, characteristics=None,
                   relation_to_bounds="within"):
    """
    Reads a vector (subset) within the given netcdf file. The bounds and the
     characteristics define the file-intern data structure.

    :param ncdf_path: path to a netcdf file
    :param bounds: boundary (shapely.geometry.polygon.Polygon)
    :param characteristics: list of desired column names / vector attributes
    :param relation_to_bounds: spatial relation between the the geodataframe \
    and the bounds (geodataframe 'within' bounds). Choose between: 'within', \
    'contains', 'intersects', 'disjoint', 'touches', 'crosses', 'overlaps', \
    'covers'
    :return: vector subset in form of a geodataframe
    """

    # check boundary validity
    if not bounds.is_valid:
        raise ValueError("Invalid boundary")

    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get the groups that intersect the bounds
    intersecting_groups = get_vector_group_names_intersecting_bounds(
                                                              ncdf_dataset,
                                                              bounds)

    if not intersecting_groups:
        raise LookupError("No groups intersect the given bounds.")

    # check consistency of variables / vector attributes
    consistency, \
        all_variable_names = check_variable_consistency(ncdf_dataset,
                                                        intersecting_groups)

    # get all characteristic/columns if not given
    if characteristics is None:
        characteristics = all_variable_names

    # create an empty dataframe
    output_dataframe = pd.DataFrame(columns=characteristics)

    crs = None
    # loop through the groups
    for group in intersecting_groups:

        # create a temporary dataframe (all group temp. df's will be merged)
        tmp_dataframe = pd.DataFrame(columns=characteristics)

        # get the specific group
        ncdf_group = get_group(ncdf_dataset, group)

        # update crs once
        if crs is None:
            crs = CRS(ncdf_group.crs)

        # read and fill the dataframe with the characteristics
        for characteristic in characteristics:
            if characteristic in ncdf_group.variables:
                features = ncdf_group.variables[characteristic][:]
            else:
                # if characteristic does not exist in the group, add nodata
                current_feature_count = ncdf_group.dimensions["features"].size
                features = current_feature_count * [None]

            tmp_dataframe[characteristic] = features

        # add temp df to general df
        output_dataframe = pd.concat([output_dataframe, tmp_dataframe])

    # convert pandas dataframe with wkt to geodataframe
    output_dataframe.geometry = output_dataframe.geometry.apply(wkt.loads)
    output_geodataframe = gpd.GeoDataFrame(output_dataframe,
                                           geometry="geometry",
                                           crs=crs)

    # use the operator to select only the part of the geodataframe with the
    # spatial relation to the bounds
    try:
        operator_call = getattr(output_geodataframe, relation_to_bounds)
    except AttributeError:
        raise AttributeError("The function read_by_bounds "
                             "has no operator '{}'".format(relation_to_bounds))

    output_geodataframe = output_geodataframe[operator_call(bounds)]

    # close the dataset
    ncdf_dataset.close()

    return output_geodataframe[~output_geodataframe.is_empty]


def read_by_attribute(ncdf_path, characteristic, characteristic_value,
                      query='='):
    """
    Reads a vector (subset) within the given netcdf file by querying a specific
    characteristic / vector attribute. For example: characteristic_value=5000,
    characteristic="area", query='>' will give you all features with the
    characteristic 'area' being bigger than (>) the characteristic_value 5000.
    
    :param ncdf_path: path to a netcdf file
    :param characteristic: desired column name / vector attribute
    :param characteristic_value: desired value for the query
    :param query: The relation between the characteristic and the \
    characteristic_value. The available query options are: >, <, >=, <=, =
    :return: vector subset in form of a geodataframe
    """

    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get all existing group names
    all_groups = list(ncdf_dataset.groups)

    # check if all groups have the same variables / vector attributes
    # and get all variable names
    consistency, \
        all_characteristics = check_variable_consistency(ncdf_dataset,
                                                         all_groups)

    # create an empty dataframe
    output_dataframe = pd.DataFrame(columns=all_characteristics)

    # convert the query argument to the respective python operator
    query_operators = {
                        '>': operator.gt,
                        '<': operator.lt,
                        '>=': operator.ge,
                        '<=': operator.le,
                        '=': operator.eq
                      }

    crs = None
    # loop through all groups
    for group in all_groups:

        # get the specific group
        ncdf_group = get_group(ncdf_dataset, group)

        # update the coordinate reference system once
        if crs is None:
            crs = CRS(ncdf_group.crs)

        # get the characteristic / netcdf variable
        try:
            group_fid = ncdf_group.variables[characteristic]
        except AttributeError:
            raise AttributeError("Attribute {} does not exist in group "
                                 "{}".format(characteristic, group))

        # get all features that match the query
        if query not in query_operators.keys():
            raise KeyError("{} is not a valid query".format(query))
        matches = query_operators[query](group_fid[:], characteristic_value)

        # read all characteristics / netcdf variables of the matches and fill
        # the output dataframe
        for characteristic_name in all_characteristics:
            if characteristic in ncdf_group.variables:
                try:
                    data_matches = \
                        ncdf_group.variables[characteristic_name][matches]
                except IndexError:
                    data_matches = \
                     ncdf_group.variables[characteristic_name][:][matches.data]
            else:
                # if characteristic does not exist in the group, add nodata
                data_matches = len(matches) * [None]
            output_dataframe[characteristic_name] = data_matches

    # convert pandas dataframe with wkt to geodataframe
    output_dataframe.geometry = output_dataframe.geometry.apply(wkt.loads)
    output_geodataframe = gpd.GeoDataFrame(output_dataframe,
                                           geometry="geometry")
    output_geodataframe.crs = crs

    # close the dataset
    ncdf_dataset.close()

    return output_geodataframe[~output_geodataframe.is_empty]


def create_by_group(geodataframe, ncdf_path, group, attributes):
    """
    Writes a geodataframe into a new netcdf file. The group
    defines the file-intern data structure.

    :param geodataframe: Geodataframe that should get written into the netcdf
    :param ncdf_path: path to a netcdf file
    :param group: netcdf group name
    :param attributes: dictionary including all metadata
    """

    if os.path.exists(ncdf_path):
        warn("{} already exists and cannot be created. Please use the"
             "function 'upsert_by_group'".format(ncdf_path), RuntimeWarning)

    # create new netcdf
    ncdf_dataset = write_netcdf(ncdf_path)

    # close the dataset
    ncdf_dataset.close()

    if group in ncdf_dataset.groups:
        raise NameError("Group {} already exists and cannot be created. "
                        "Please use the function "
                        "'upsert_by_group'".format(group))

    ncdf_dataset = write_netcdf(ncdf_path)
    set_group(ncdf_dataset, group)
    ncdf_dataset.close()

    upsert_by_group(geodataframe, ncdf_path, group, attributes=attributes)


def upsert_by_group(geodataframe, ncdf_path, group, attributes=None):
    """
    Adds a geodataframe into an existing netcdf file. The group
    defines the file-intern data structure.

    :param geodataframe: Geodataframe that should get written into the netcdf
    :param ncdf_path: path to a netcdf file
    :param group: netcdf group name
    :param attributes: dictionary including all metadata
    """

    if not os.path.exists(ncdf_path):
        raise NameError("{} does not exists. Please use the"
                        "function 'create_by_group'".format(ncdf_path))

    # get all features where the geometry already exists
    # and update_by_attribute
    geodataframe = update_existing_vector_features(ncdf_path, geodataframe,
                                                   group)

    # create new netcdf or open it for writing
    ncdf_dataset = write_netcdf(ncdf_path)

    if group not in ncdf_dataset.groups:
        ncdf_dataset.close()
        raise NameError("Group {} does not exist yet. "
                        "Please use the function "
                        "'create_by_group'".format(group))

    # orientate into the specific group
    ncdf_group = get_group(ncdf_dataset, group)

    # create dimensions if they do not exist
    characteristics = list(geodataframe.keys())
    # make sure that "geometry" is the last element
    characteristics += [characteristics.pop(characteristics.index("geometry"))]

    # "characteristics" is not len(characteristics) because it can be altered
    # if new attributes get created
    dimensions = {"features": None, "characteristics": None}
    create_dimensions(dimensions, ncdf_group)

    # get the current feature count
    current_feature_count = ncdf_group.dimensions["features"].size

    # get only geodataframe features which are within the group bbox
    if ncdf_group.variables:
        group_bbox = get_group_bbox(ncdf_dataset, group)
        geodataframe = \
            geodataframe[geodataframe.geometry.centroid.within(group_bbox)]

    # for each characteristic / vector attribute
    for characteristic in characteristics:

        # get the datatype of the characteristic
        characteristic_dtype = geodataframe[characteristic].dtype
        if characteristic_dtype != np.number \
                and characteristic_dtype != np.int \
                and characteristic_dtype != np.float:
            characteristic_dtype = str

        # create or get the group variable
        if characteristic not in ncdf_group.variables:

            ncdf_variable = ncdf_group.createVariable(characteristic,
                                                      characteristic_dtype,
                                                      ("features",))
        else:
            ncdf_variable = ncdf_group.variables[characteristic]

        if characteristic == "geometry":
            fill = np.array(geodataframe.geometry.apply(lambda g: g.wkt))
        else:
            fill = np.array(geodataframe[characteristic])

        ncdf_variable[current_feature_count:] = fill

    # fill the attributes of the group
    if "crs" not in ncdf_group.__dict__:
        ncdf_group.crs = CRS(geodataframe.crs).to_wkt()

    if attributes:
        for key, value in attributes.items():

            # special cases
            if value is None:
                continue
            elif type(value) == bool:
                value = str(value)
            elif type(value) == dict:
                value = json.dumps(value)

            # overwrite existing attributes
            if key in ncdf_group.__dict__:
                del ncdf_group.__dict__[key]
                ncdf_group.__dict__[key] = value
            else:
                ncdf_group.key = value
                ncdf_group.renameAttribute("key", key)

    # close the dataset
    ncdf_dataset.close()


def upsert_by_bounds(geodataframe, ncdf_path, bounds,
                     relation_to_bounds="within"):
    """
    Adds all geodataframe features in relation to the bounds
    into an existing netcdf file. The bounds also define in which file-intern
    data structure (groups) the data will be stored.

    :param geodataframe: Geodataframe that should get written into the netcdf
    :param ncdf_path: path to a netcdf file
    :param bounds: boundary (shapely.geometry.polygon.Polygon)
    :param relation_to_bounds: spatial relation between the the geodataframe \
    and the bounds (geodataframe 'within' bounds). Choose between: 'within', \
    'contains', 'intersects', 'disjoint', 'touches', 'crosses', 'overlaps', \
    'covers'
    """

    # open existing netcdf file for writing
    if not os.path.exists(ncdf_path):
        raise OSError("{} does not exist yet. The function update_by_bounds "
                      "only updates given data.".format(ncdf_path))

    ncdf_dataset = write_netcdf(ncdf_path)

    # get the groups that intersect the bounds
    intersecting_groups = get_vector_group_names_intersecting_bounds(
                                                              ncdf_dataset,
                                                              bounds)

    if not intersecting_groups:
        raise LookupError("No groups intersect the given bounds.")

    # select the geodataframe features "within" (operator) the bounds
    try:
        operator_call = getattr(geodataframe.geometry.centroid,
                                relation_to_bounds)
    except AttributeError:
        raise AttributeError("The function update_by_bounds "
                             "has no operator '{}'".format(operator))

    geodataframe = geodataframe[operator_call(bounds)]

    # get the bounding box of each group that intersects the bounds
    all_group_bboxes = [get_group_bbox(ncdf_dataset, group)
                        for group in intersecting_groups]

    # close dataset
    ncdf_dataset.close()

    # loop through the groups that intersect the bounds
    for group, group_bbox in zip(intersecting_groups, all_group_bboxes):

        # get geodataframe features that are within the group
        selected_group_features = \
            geodataframe[geodataframe.geometry.centroid.within(group_bbox)]

        # write the selected geodataframe features into the respective group
        upsert_by_group(selected_group_features, ncdf_path, group)


def upsert_by_geodataframe(geodataframe, ncdf_path):
    """
    Writes all geodataframe features into an existing netcdf file.
    The outer bounds of the geodataframe define in which file-intern
    data structure (groups) the data will be stored.

    :param geodataframe: Geodataframe that should get written into the netcdf
    :param ncdf_path: path to a netcdf file
    """

    if not os.path.exists(ncdf_path):
        raise NameError("{} does not exists. Please use the"
                        "function 'create_by_group'".format(ncdf_path))

    # get outer bounds of the geodataframe
    minx, miny, maxx, maxy = geodataframe.total_bounds
    bounds = Polygon([[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny]])

    upsert_by_bounds(geodataframe, ncdf_path, bounds,
                     relation_to_bounds="within")


def update_by_attribute(ncdf_path, characteristic, characteristic_value,
                        updated_characteristic, updated_value, query='='):
    """
    Updates all geodataframe features who's characteristic matches the
    characteristic value according to the query operator with the update_value.
    For example: characteristic_value=5000,
    characteristic="area", query='>', update_value=0 will update all features
    with the characteristic 'area' being bigger than (>) the
    characteristic_value 5000 with the new value 0.

    :param ncdf_path: path to a netcdf file
    :param characteristic: desired column name / vector attribute
    :param characteristic_value: desired value for the query
    :param updated_characteristic: characteristic that should get updated
    :param updated_value: new value for the updated_characteristic
    :param query: The relation between the characteristic and the \
    characteristic_value. The available query options are: >, <, >=, <=, =
    """

    # open existing netcdf file for writing
    if not os.path.exists(ncdf_path):
        raise OSError("{} does not exist yet. The function update_by_bounds "
                      "only updates given data.".format(ncdf_path))

    ncdf_dataset = write_netcdf(ncdf_path)

    # get all existing group names
    all_groups = list(ncdf_dataset.groups)

    query_operators = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq
    }

    # loop through all group names
    for group in all_groups:

        # get the specific group
        ncdf_group = get_group(ncdf_dataset, group)

        # get the characteristic / netcdf variable
        try:
            group_characteristic = ncdf_group.variables[characteristic]
        except AttributeError:
            raise AttributeError("Attribute {} does not exist in group "
                                 "{}".format(characteristic, group))

        # find all features who's characteristic matches the
        # characteristic value using the query operator
        if characteristic == "geometry":
            matches = []
            for geom in group_characteristic[:]:
                if wkt.loads(geom).equals(wkt.loads(characteristic_value)):
                    matches.append(True)
                else:
                    matches.append(False)
            matches = np.array(matches)
        else:
            if query not in query_operators.keys():
                raise KeyError("{} is not a valid query".format(query))
            matches = query_operators[query](group_characteristic[:],
                                             characteristic_value
                                             )

        if not np.any(matches):
            continue

        # get the update_characteristic / netcdf variable
        if updated_characteristic in ncdf_group.variables:
            updated_group_characteristic = \
                ncdf_group.variables[updated_characteristic]
        else:
            # create update_characteristic as new variable
            updated_characteristic_dtype = np.array(updated_value).dtype
            updated_group_characteristic = ncdf_group.createVariable(
                                                updated_characteristic,
                                                updated_characteristic_dtype,
                                                ("features",))

        # update the given characteristic of the matches with the given value
        try:
            updated_group_characteristic[matches] = np.array(updated_value)
        except IndexError:
            updated_group_characteristic[matches.data] = updated_value

    # close the dataset
    ncdf_dataset.close()


def update_existing_vector_features(ncdf_path, geodataframe, group):
    """
    This function compares a geodataframe with a netcdf group containing
    vector attributes in form of netCDF variables. All geometries that already
    exist will get updated while the remaining features will be returned as a
    geodataframe

    :param ncdf_path: path to the netcdf file
    :param geodataframe: GeoDataFrame
    :param group: netCDF group name
    :return: geodataframe without the features that got updated
    """

    # Get all geodataframe characteristics without the geometry (for update)
    characteristics = list(geodataframe.keys())
    characteristics.remove("geometry")

    # Read the netCDF group
    ncdf_dataset = write_netcdf(ncdf_path)
    ncdf_group = get_group(ncdf_dataset, group)

    # In case the group already has variables
    if ncdf_group.variables:

        # get a list of all geometries, that are equal between netCDF
        # and the input geodataframe
        ncdf_gdf = gpd.GeoDataFrame(gpd.GeoSeries([wkt.loads(geom)
                                                   for geom in
                                                   ncdf_group.variables[
                                                       "geometry"][:]]),
                                    columns=['geometry'])

        already_existing_features = [geom for geom in geodataframe.geometry
                                     if
                                     geom in ncdf_gdf.geometry]
        ncdf_dataset.close()

        # update_by_attribute for all geometries that already exist
        for existing_geometry in already_existing_features:
            gdf_intersection = geodataframe[geodataframe.geometry ==
                                            existing_geometry]
            for characteristic in characteristics:

                feature = list(gdf_intersection[characteristic])[0]

                update_by_attribute(ncdf_path, "geometry",
                                    wkt.dumps(existing_geometry),
                                    characteristic, feature, query='=')

        # remove all features that were updated from the input geodataframe,
        # because the rest will probably be added (upsert_by_group)
        for existing_geometry in already_existing_features:
            geodataframe = geodataframe[geodataframe.geometry !=
                                        existing_geometry]
    else:
        ncdf_dataset.close()

    return geodataframe
