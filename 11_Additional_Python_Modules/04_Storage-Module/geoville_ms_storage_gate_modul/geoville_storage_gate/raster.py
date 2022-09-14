import os
import numpy as np
from warnings import warn

from lib.storage_utils import read_netcdf, write_netcdf, \
                              set_group, get_group, \
                              get_raster_group_names_intersecting_bounds, \
                              write_raster, write_raster_by_group, \
                              check_attribute_consistency, \
                              get_temporal_bounds, get_variable_subset


def read_by_group(ncdf_path, start_time, end_time, group,
                  array_variable="raster"):
    """
    Reads a raster (subset) within the given netcdf file. The group and
    array_variable define the file-intern data structure.

    :param ncdf_path: path to a netcdf file
    :param group: netcdf group name
    :param start_time: start date (e.g. 2019-12-31)
    :param end_time: end date (e.g. 2019-12-31)
    :param array_variable: Name of the variable within the netcdf group that \
    represents the raster data in form of an array
    :return: raster subset in form of a numpy array \
    and the respective Affine transformation
    """
    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get the specific group if given
    ncdf_group = get_group(ncdf_dataset, group)

    # get the temporal bounds
    time_min, time_max = get_temporal_bounds(ncdf_group, start_time, end_time)

    # read the subset
    try:
        ncdf_array, ncdf_affine = get_variable_subset(ncdf_group,
                                                      array_variable,
                                                      time_min,
                                                      time_max,
                                                      None)
    except Exception as err:
        ncdf_dataset.close()
        raise Exception(err)


    # get attributes of the group
    attribute_names = ncdf_group.ncattrs()
    attribute_values = [ncdf_group.getncattr(attribute)
                        for attribute in attribute_names]
    ncdf_attributes = dict(zip(attribute_names, attribute_values))

    # update attributes with subset transformation and timestamps
    timestamps = ncdf_group.variables["time"][time_min:time_max]
    if "time" in ncdf_attributes.keys():
        current_time = ncdf_attributes["time"]
        timestamps = list(set(current_time + timestamps))

    ncdf_attributes.update(transform=ncdf_affine, time=timestamps)

    # close the dataset
    ncdf_dataset.close()

    return ncdf_array, ncdf_attributes


def read_by_bounds(ncdf_path, start_time, end_time, bounds,
                   array_variable="raster"):
    """
    Reads a raster (subset) within the given netcdf file. The bounds and
    array_variable define the file-intern data structure. The bounds come from
    a vector dataset.

    :param ncdf_path: path to a netcdf file
    :param bounds: boundary for the subset (shapely.geometry.polygon.Polygon)
    :param start_time: start date (e.g. 2019-12-31)
    :param end_time: end date (e.g. 2019-12-31)
    :param array_variable: Name of the variable within the netcdf group that \
    represents the raster data in form of an array
    :return: raster subset in form of a numpy array \
    and the respective Affine transformation
    """

    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get the groups that intersect the bounds
    intersecting_groups = \
        get_raster_group_names_intersecting_bounds(ncdf_dataset, bounds)

    if not intersecting_groups:
        raise LookupError("No groups intersect the given bounds.")

    # check consistency
    check_attribute_consistency(ncdf_dataset, intersecting_groups)

    # get attributes of the group
    first_group = get_group(ncdf_dataset, intersecting_groups[0])
    attribute_names = first_group.ncattrs()
    attribute_values = [first_group.getncattr(attribute)
                        for attribute in attribute_names]
    ncdf_attributes = dict(zip(attribute_names, attribute_values))

    # read rasters by group
    ncdf_arrays = []
    for group_name in intersecting_groups:

        # get the specific group if given
        ncdf_group = get_group(ncdf_dataset, group_name)

        # get the temporal bounds
        time_min, time_max = get_temporal_bounds(ncdf_group, start_time,
                                                 end_time)

        # read the subset
        try:
            ncdf_subset, ncdf_affine = get_variable_subset(ncdf_group,
                                                           array_variable,
                                                           time_min,
                                                           time_max,
                                                           bounds)
        except Exception as err:
            ncdf_dataset.close()
            raise Exception(err)

        # replace nodata value with nan
        ncdf_subset = ncdf_subset.astype(float)
        ncdf_subset[ncdf_subset == ncdf_attributes["nodata"]] = np.nan

        ncdf_arrays.append(ncdf_subset)

        # update attributes with subset transformation and timestamps
        timestamps = ncdf_group.variables["time"][time_min:time_max]
        if "time" in ncdf_attributes.keys():
            current_time = ncdf_attributes["time"]
            timestamps = list(set(current_time + timestamps))

        ncdf_attributes.update(transform=ncdf_affine, time=timestamps)

    # merge rasters
    ncdf_array = np.nanmax(ncdf_arrays, axis=0)

    # update attributes with subset transformation and shape
    count, height, width = ncdf_array.shape
    ncdf_attributes.update(count=count, height=height, width=width)

    # correct datatype and nodata value
    ncdf_array[np.isnan(ncdf_array)] = ncdf_attributes["nodata"]
    ncdf_array = ncdf_array.astype(ncdf_attributes["dtype"])

    # close the dataset
    ncdf_dataset.close()

    return ncdf_array, ncdf_attributes


def create_by_group(array, profile, ncdf_path, group, start_time,
                    end_time, array_variable="raster"):
    """
    Creates a new netcdf file with a new group in which the array will be saved
    with the identifier "array_variable". The numpy array needs to have an
    axis=0 of the same length than the time range in days
    (start_time - end_time).

    :param array: numpy array that contains the new data to write
    :param profile: dictionary including all metadata (rasterio's profile)
    :param ncdf_path: path to the netcdf file
    :param group: group name of the netcdf dataset \
    where the new array or the update will take place
    :param start_time: start date (e.g. 2019-12-31)
    :param end_time: end date (e.g. 2019-12-31)
    :param array_variable: Name of the variable within the netcdf group that \
    represents the raster data in form of an array
    """

    if os.path.exists(ncdf_path):
        warn("{} already exists. Please use the "
             "function 'upsert_by_group'".format(ncdf_path), RuntimeWarning)

    # create new netcdf
    ncdf_dataset = write_netcdf(ncdf_path)

    if group in ncdf_dataset.groups:
        ncdf_dataset.close()
        raise NameError("Group {} already exists and cannot be created. "
                        "Please use the function "
                        "'upsert_by_group'".format(group))
    else:
        ncdf_dataset.close()

    write_raster_by_group(array, profile, ncdf_path, group, start_time,
                          end_time, array_variable=array_variable)


def upsert_by_group(array, profile, ncdf_path, group, start_time,
                    end_time, array_variable="raster"):
    """
    Adds to or updates an existing group within an existing netCDF file.
    The array will be saved with the identifier "array_variable". The numpy
    array needs to have an axis=0 of the same length than the time range in
    days (start_time - end_time).

    :param array: numpy array that contains the new data to write
    :param profile: dictionary including all metadata (rasterio's profile)
    :param ncdf_path: path to the netcdf file
    :param group: group name of the netcdf dataset \
    where the new array or the update will take place
    :param start_time: start date (e.g. 2019-12-31)
    :param end_time: end date (e.g. 2019-12-31)
    :param array_variable: Name of the variable within the netcdf group that \
    represents the raster data in form of an array
    """

    if not os.path.exists(ncdf_path):
        raise NameError("{} does not exists. Please use the"
                        "function 'create_by_group'".format(ncdf_path))

    # open netcdf for writing
    ncdf_dataset = write_netcdf(ncdf_path)

    if group not in ncdf_dataset.groups:
        ncdf_dataset.close()
        raise NameError("Group {} does not exist. "
                        "Please use the function "
                        "'create_by_group'".format(group))
    else:
        ncdf_dataset.close()

    write_raster_by_group(array, profile, ncdf_path, group, start_time,
                          end_time, array_variable=array_variable)


def update_by_bounds(array, profile, ncdf_path, bounds, start_time,
                     end_time, array_variable="raster"):
    """
    Updates a raster (subset) within the given/new netcdf file. The bounds and
    array_variable define the file-intern data structure. The bounds come from
    a vector dataset.

    :param array: numpy array that contains the new data to write
    :param profile: dictionary including all metadata (rasterio's profile)
    :param ncdf_path: path to the netcdf file
    :param bounds: boundary (shapely.geometry.polygon.Polygon) \
    where the new array or the update will take place
    :param start_time: start date (e.g. 2019-12-31)
    :param end_time: end date (e.g. 2019-12-31)
    :param array_variable: Name of the variable within the netcdf group that \
    represents the raster data in form of an array
    """

    # create new netcdf or open it for writing
    if not os.path.exists(ncdf_path):
        raise OSError("{} does not exist yet. The function update_by_bounds "
                      "only updates given data.".format(ncdf_path))
    ncdf_dataset = write_netcdf(ncdf_path)

    # get the groups that intersect the bounds
    intersecting_groups = \
        get_raster_group_names_intersecting_bounds(ncdf_dataset, bounds)

    if not intersecting_groups:
        raise LookupError("No groups intersect the given bounds.")

    # check consistency
    check_attribute_consistency(ncdf_dataset, intersecting_groups)

    for group_name in intersecting_groups:

        # orientate into the specific group
        ncdf_group = get_group(ncdf_dataset, group_name)

        write_raster(array, profile, ncdf_group, start_time, end_time,
                     array_variable=array_variable, bounds=bounds)

    # close the dataset
    ncdf_dataset.close()


def get_dates(ncdf_path, group):
    """
    Returns a list of dates that represent the temporal dimension of a given
    group.

    :param ncdf_path: path to the netcdf file
    :param group: group name of the netcdf dataset
    :return: list of date strings
    """

    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # get the specific group if given
    ncdf_group = get_group(ncdf_dataset, group)

    # get the time variable
    time_dimension = list(ncdf_group.variables["time"][:])

    # close the dataset
    ncdf_dataset.close()

    return time_dimension
