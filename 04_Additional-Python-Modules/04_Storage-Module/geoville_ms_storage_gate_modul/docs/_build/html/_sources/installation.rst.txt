Installation
============

Dependencies
------------
The GeoVille Storage Gate has the following dependencies:

- numpy
- pandas
- geopandas
- shapely
- rasterio
- rasterstats
- affine
- netCDF4

Another indirect dependency is **GDAL**

Installing with pip
-------------------

You can install the GeoVille Storage Gate directly from Bitbucket_ with pip::

    pip install https://<USER>:<PASSWORD>@bitbucket.org/geoville/geoville_ms_storage_gate_modul/get/master.zip


.. _Bitbucket:
    https://bitbucket.org/geoville/geoville_ms_storage_gate_modul/src/master/


Installing from source
----------------------

You may install the latest version by cloning the Bitbucket_ repository
and using pip to install from the local directory::

    git clone git@bitbucket.org:geoville/geoville_ms_storage_gate_modul.git
    cd geoville_ms_storage_gate_modul
    pip install -e .
