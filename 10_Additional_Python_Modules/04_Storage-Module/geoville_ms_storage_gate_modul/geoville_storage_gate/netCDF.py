import os

from lib.storage_utils import read_netcdf


def delete_netcdf(ncdf_path):
    """
    This function deletes a netcdf file

    :param ncdf_path: Path incl. file name of the netCDF file that will be \
    deleted
    """
    if not ncdf_path.endswith(".nc"):
        raise OSError("Deleting the data format failed. The given path has "
                      "to end with '.nc'")
    if not os.path.exists(ncdf_path):
        raise OSError("{} does not exist".format(ncdf_path))

    os.remove(ncdf_path)


def merge_netcdf_to_data_cube(ncdf_paths, ncdf_data_cube):
    """
    This function merges several netcdf files of the same information and
    spatial extent. The only difference is the timestamp.

    :param ncdf_paths: list of paths to .nc files
    :param ncdf_data_cube: path to the .nc file that will contain the merge
    """
    os.system("ncecat -O -h -x -v lambert_azimuthal_equal_area -u time "
              "{} {}".format(" ".join(ncdf_paths), ncdf_data_cube))


def convert_geotiff_to_netcdf(gtiff_path, ncdf_path):
    """
    Converts a GeoTiff file to a netcdf file

    :param gtiff_path: geotiff path incl. file name
    :param ncdf_path: path to the output netcdf file
    """

    os.system("gdal_translate -of netCDF -co WRITE_LONGLAT=YES "
              "{} {}".format(gtiff_path, ncdf_path))


def get_group_names(ncdf_path):
    """
    Returns a list with all the group names within a netcdf file

    :param ncdf_path: path to a netcdf file
    :return: list with all group names within the netcdf file
    """
    # read netcdf file
    ncdf_dataset = read_netcdf(ncdf_path)

    # list of group names
    group_names = list(ncdf_dataset.groups)

    # close the dataset
    ncdf_dataset.close()

    return group_names
