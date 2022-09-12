How to work with raster data
============================

When writing and reading a raster into a netCDF file, there are several
options. The following instructions shall serve as a guide.


Create a netCDF file or group
-----------------------------

When writing a raster into a netCDF file or a group that does not exist yet,
only ``create_by_group`` can be used. This function creates a netCDF file in
case it does not exist. Moreover, the defined group will be created before
the raster gets inserted. Therefore, the group will have the metadata and
dimensions of the raster's profile.

Many programs that create raster products end by having a numpy array.

If that array gets stored as a GeoTiff, the module ``rasterio`` can easily
read it as a numpy array again:

.. code-block:: python

        import rasterio

        with rasterio.open("example.tif") as src:
            array = src.read()
            profile = src.profile()

Now that we have a numpy array and the raster's metadata (profile), we can
store it into a netCDF file for the first time.

.. code-block:: python

        create_by_group(array,
                        profile,
                        ncdf_path="example.nc",
                        group="example_group_name",
                        start_time="2019-05-01",
                        end_time="2019-05-10",
                        array_variable="raster")

Now we created the example netCDF file "example.nc" with the group
"example_group_name". This group does contain the array as a variable with
the name "raster". Furthermore, we defined the start and the end date,
that describe the layers of the given array. In our example we defined a range
of 10 days (2019-05-01 - 2019-05-10). Hence, the array we write also needs to
have 10 layers (axis 0 = 10).

The dictionary "profile" serves to save the geospatial metadata as group
attributes. It contains the geotransformation, the coordinate reference system,
etc. Note that the profile needs to contain "nodata", "transform",
"dtype" and "crs" in order to reuse it later again (see rasterio-profile_).

.. _rasterio-profile:
    https://rasterio.readthedocs.io/en/latest/topics/profiles.html

Upsert using the group name
---------------------------

After creating a netCDF file and a group, the entire group can be upserted.
An "upsert" means that if the timestamp already exists, the raster will get
replaced, otherwise it gets inserted.
In case of the following example, the raster that gets written represents the
two dates: "2019-04-30", "2019-05-01". Again, the array needs to have
the same z-axis than the given time range which is two days in this example.
The first date does not exist yet and thus gets added while the second date
already exists, so it gets updated.

.. code-block:: python

    upsert_by_group(array,
                    profile,
                    ncdf_output_path,
                    "test_raster_group",
                    "2019-04-30",
                    "2019-05-01",
                    array_variable="raster")

Update using bounds
-------------------

If you want to update an area that might intersect several groups,
you need to use ``update_by_bounds`` as follows. Note that this function is an
update only and no upsert.

.. code-block:: python

        example_bounds = Polygon([[661697.166128716, 4320223.863762978],
                                  [660697.2823883237, 4320130.124662316],
                                  [660603.5432876621, 4321296.655692774],
                                  [661738.8279512323, 4321234.162958999],
                                  [661697.166128716, 4320223.863762978]])

        update_by_bounds(array_for_update,
                       profile,
                       ncdf_path="example.nc",
                       bounds=example_bounds,
                       start_time="2019-05-04",
                       end_time="2019-05-04",
                       array_variable="raster")

For an update, we use the same "ncdf_path" as before. The "array_for_update"
can be bigger than the bounds, but only the data within the bounds will be used
for an update. Again, the array needs to have the same z-axis than the given
time range which is one day in this example. So we update only one day
(2019-05-04) within the "example_bounds". Note that the coordinate reference
system (crs) of the bounds you use, has to be the same than the crs of the
netCDF dataset. The same goes for the metadata of the "profile". You cannot use
another datatype or nodata value when updating an existing raster dataset.
Moreover, the "array_variable" of the update needs to coincide with the
"array_variable" of the raster within the netCDF file that will get updated.
In case the bounds intersect more than one netCDF group, each of those groups
will get updated respectively without changing the dimensions.

Read using the group name
-------------------------

Reading the raster of an entire netCDF group is as easy as defining the
path to the netCDF file ("ncdf_path"), the correct "group" name and the
variable name ("array_variable") of the data you want to obtain. Furthermore,
the start and end date selects only the layers you want to have from the entire
data cube.

.. code-block:: python

        array, profile = read_by_group(ncdf_path="example.nc",
                                       start_time="2019-05-02",
                                       end_time="2019-05-08",
                                       group="example_group_name",
                                       array_variable="raster")

In our example, we obtain a numpy array with 7 layers, one for each day.
Additionally we get the profile returned so that we can write the numpy array
into any other format we want, such as a GeoTiff:

.. code-block:: python

        import rasterio

        with rasterio.open("example_subset.tif", "w", **profile) as dst:
            for lid, layer in enumerate(array):
                dst.write(layer, lid+1)

The profile also contains a list of date strings referring to the layers of the
array. For example, if the start date is 2019-05-02 and the end date is
2019-05-08, but we only get 4 layers instead of 7, we can assume, that the
netCDF file does not have all the dates. If we want to know which layer
corresponds to which of the possible 7 dates, we can check the profile.

Read using bounds
-----------------

If we do not care about the group names or want to have a subset of data that
can even intersect more than one group, the function ``read_by_bounds`` can
be used.

It is basically the same than ``read_by_group`` but instead of a group name,
a shapely Polygon representing a boundary of interest is required.

.. code-block:: python

        example_bounds = Polygon([[661697.166128716, 4320223.863762978],
                                  [660697.2823883237, 4320130.124662316],
                                  [660603.5432876621, 4321296.655692774],
                                  [661738.8279512323, 4321234.162958999],
                                  [661697.166128716, 4320223.863762978]])

        array, profile = read_by_bounds(ncdf_path="example.nc",
                                       start_time="2019-05-02",
                                       end_time="2019-05-08",
                                       bounds=example_bounds,
                                       array_variable="raster")

