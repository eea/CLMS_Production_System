How to work with netCDF files
=============================

This section contains basic deletion and conversion functions as well as
helpful tools to get an insight into the netCDF data structure.

Get all netCDF group names
--------------------------

``get_group_names`` returns a list of all group names that are within a
netCDF file.

.. code-block:: python

        netcdf_group_names = get_group_names("example.nc")

