How to work with vector data
=============================

When writing and reading a vector into a netCDF file, there are three options:
    - by using the group name
    - by using a boundary (shapely Polygon)
    - by using a query (e.g. "area">5000)

Create a netCDF file or group
-----------------------------

When writing a vector into a netCDF file or a group that does not exist yet,
only ``create_by_group`` can be used. This function creates a netCDF file in
case it does not exist. Moreover, the defined group will be created before
the vector gets inserted. Therefore, the group will have the coordinate
reference system and outer bounds of the vector.

Many programs that create vector products end by having a GeoDataFrame.

If that GeoDataFrame gets stored as a Shapefile or another vector file format,
the module ``geopandas`` can easily read it as a GeoDataFrame again:

.. code-block:: python

        import geopandas as gpd

        geodataframe = gpd.read_file("example.shp")

Now that we have a GeoDataFrame, we can store it into a netCDF file for the
first time.

.. code-block:: python

        create_by_group(geodataframe,
                       ncdf_path="example.nc",
                       group="example_group_name",
                       attributes={"crs": geodataframe.crs})

Now we created the example netCDF file "example.nc" with the group
"example_group_name". This group does contain the GeoDataFrame in form of a
variable for each vector attribute/column.

The dictionary "attributes" servers to save the geospatial metadata as group
attributes. Note that it needs to contain the "crs" (see geopandas-crs_).

.. _geopandas-crs:
    https://geopandas.org/reference.html?highlight=crs#geopandas.GeoDataFrame.crs

Upsert using the group name
---------------------------

After creating a netCDF file and a group, the group can be upserted.
An "upsert" means that if a geometry already exists, the vector feature will
get updated, otherwise the feature gets inserted. It is also possible that the
new geodataframe has a vector attribute/column that does not exist yet.

.. code-block:: python

        upsert_by_group(geodataframe_for_upsert,
                        ncdf_path="example.nc",
                        group="example_group_name")

Upsert using bounds
-------------------

If you want to upsert an area that might intersect several groups,
you need to use ``upsert_by_bounds`` as follows. Again, it is possible that the
new geodataframe has a vector attribute/column that does not exist yet. Not all
netCDF groups will get this new column, but only the groups that stay in a
relation to the bounds.

.. code-block:: python

        example_bounds = Polygon([[661697.166128716, 4320223.863762978],
                                  [660697.2823883237, 4320130.124662316],
                                  [660603.5432876621, 4321296.655692774],
                                  [661738.8279512323, 4321234.162958999],
                                  [661697.166128716, 4320223.863762978]])

        upsert_by_bounds(geodataframe_for_upsert,
                        ncdf_path="example.nc",
                        bounds=example_bounds,
                        relation_to_bounds="intersects")

For the upsert, we use the same "ncdf_path" as before. The
"geodataframe_for_update" can be bigger than the bounds, but only
the data in relation to the bounds ("relation_to_bounds") will be used for an
upsert. If "relation_to_bounds" is "intersects" as in our example, all features
from the "geodataframe_for_update" will be used that intersect the bounds.
Note that the coordinate reference system (crs) of the bounds you use, has to
be the same than the crs of the netCDF dataset. In case the bounds intersect
more than one netCDF group, each of those groups will get upserted respectively
without changing the dimensions. Thereby, all features of
"geodataframe_for_update" within the bounds, who's centroid fall
within the group bounding box will be upserted in the respective netCDF group.
The bounding box of a group refers to the outer bounds of all features that
were written when the group was created (``create_by_group``).

Update using a query
--------------------

Besides upserting a vector with a group name or bounds, you can also query
features and update them. In this case, it is an update only and no upsert.
For example, if you want to update the characteristic/vector-attribute "name"
of all features with an area bigger than 5000 m² to "big", you can do the
following:

.. code-block:: python

    update_by_attribute(ncdf_path="example.nc",
                       characteristic="area",
                       characteristic_value=5000,
                       updated_value="name",
                       updated_value="big",
                       query='>')

The function automatically searches for all queried features in the defined
netCDF file, independent of the group they are stored in.
Note that both characteristics ("characteristic" and "updated_characteristic")
need to exist already.

In case a feature shall get **deleted**, you can update it with an empty
geometry:

.. code-block:: python

    updated_value="geometry"
    updated_value=wkt.dumps(Polygon([]))

Read using the group name
-------------------------

Reading the vector of an entire netCDF group is as easy as defining the
path to the netCDF file ("ncdf_path") and the correct "group" name.
If we define "characteristics", we can even limit the returned vector
attributes. For example, if we only want the name and the geometry, we define:

characteristics=["name", "geometry"]

However, in our example we use None to automatically get all characteristics.

.. code-block:: python

        geodataframe = read_by_group(ncdf_path="example.nc",
                                     group="example_group_name",
                                     characteristics=None)

As a result we obtain a GeoDataFrame.
In case we want to write the GeoDataFrame into any other format, such as a
Shapefile, we can do as follows:

.. code-block:: python

        geodataframe.to_file("example_subset.shp")

Read using bounds
-----------------

If we do not care about the group names or want to have a subset of data that
can even intersect more than one group, the function ``read_by_bounds`` can
be used.

It is basically the same than ``read_by_group`` but instead of a group name,
a shapely Polygon representing a boundary of interest is required. By defining
the additional "relation_to_bounds" argument, only the features in
relation to the bounds ("relation_to_bounds") will be read. If
"relation_to_bounds" is "intersects" as in our example, all features from the
netCDF file will be read that intersect the bounds.

If we define "characteristics", we can even limit the returned vector
attributes. For example, if we only want the name and the geometry, we define:

characteristics=["name", "geometry"]

However, in our example we use None to automatically get all characteristics.
In case some of the groups that stay in the defined relation to the bounds have
more vector attributes/columns than the rest, the output geodataframe will
contain the maximum possible set. Hence, features that miss certain vector
attributes will have it filled with no-data.

.. code-block:: python

        example_bounds = Polygon([[661697.166128716, 4320223.863762978],
                                  [660697.2823883237, 4320130.124662316],
                                  [660603.5432876621, 4321296.655692774],
                                  [661738.8279512323, 4321234.162958999],
                                  [661697.166128716, 4320223.863762978]])

        geodataframe = read_by_bounds(ncdf_path="example.nc",
                                      bounds=example_bounds,
                                      characteristics=None,
                                      relation_to_bounds="intersects")

Read using a query
------------------

Besides reading a vector with a group name or bounds, you can also read
features using a specific query. For example, if you want to read all features
who's characteristic/vector-attribute "area" is bigger than 5000 m², you can do
the following:

.. code-block:: python

    read_by_attribute(ncdf_path="example.nc",
                      characteristic="area",
                      characteristic_value=5000,
                      query='>')

The function automatically searches for all queried features in the defined
netCDF file, independent of the group they are stored in. Note that a geometry
cannot be queried.

Crop To Bounds
--------------
Besides reading vector data from and writing vector data into netCDF files,
the function ``crop_to_bounds`` enables the user to crop a GeoDataFrame to
a boundary. This is often helpful after using ``read_by_bounds`` in order to
crop the read geometries to the boundary.

.. code-block:: python

        example_bounds = Polygon([[171294, 509586],
                                  [408599, 513476],
                                  [308101, 224301],
                                  [132392, 336470]])
        cropped_geodataframe = crop_to_bounds(geodataframe,
                                              bounds=example_bounds)
