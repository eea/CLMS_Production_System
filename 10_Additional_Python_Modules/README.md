# Additional Python Modules

---

## Contributors
* Johannes Schmid
* Michel Schwandner

## Databse Module
This module abstracts a PostgreSQL database connector and provides several functions to read from and
write into tables. The provided methods are:

 * read one row from a query
 * read all rows from a query
 * read many (a specific number of) rows from a query
 *execute commands such as insert, update, create, drop, delete, etc

---

## Logging Module
The logging module is a Python module which simplifies logging from within Python code. It takes the log
messages, including the log level, and sends them to the logging queue (RabbitMQ). This module helps to
simplify the code, as it does not require communication with the logging API via HTTP. To send messages to
the queue, the RabbitMQ module described here further below is used.


---

## RabbitMQ Module
This Python module provides the basic implementation to retrieve messages from and publish messages to
RabbitMQ queues. It consists of the classes BaseReceiver and Publisher. The Publisher makes it very simple
to send a message to a queue, as can be identified by its name. A message can be everything from a string to
a number to a more complex object like a dictionary. The BaseReceiver on the other hand can listen to a
queue and retrieve messages whenever there are some in the queue

---

## Storage Gate Module
The CLC+ Backbone products consist of a large amount of data and require an efficient storage system.
Hence, it was decided to use netCDF files which are basically HDF5 files for scientific use. HDF stands for
Hierarchical Data Format. As the name states, the files have an internal data structure. Each HDF5 or netCDF
file can include several groups and even subgroups. Moreover, additional information on the groups as well
as on the elements within the groups are stored within the hierarchical data format. One big advantage of
this format (HDF5 and netCDF) is the memory efficient usage. Data is indexed so that it does not have to be
loaded into memory until specifically required. Requesting different elements and their metadata is possible
by using respective tools.

The Python based storage module is used for reading from and writing into netCDF files in various ways. Both
general geospatial data types; raster and vector data; are supported by this module. While raster data can be read and written by using netCDF groups or a region of interest (shapely Polygon), vector data can also by
read and written by querying specific attributes (e.g. “area”>5000).

Furthermore, the module provides general functions to obtain the group names of a netCDF file or the
timestamps of a specific group in case of raster data.

## Product Ingestion
This module serves as a utility that uploads quality-checked CLC+ Backbone products to netCDF files. The product’s netCDF files can then be accessed via the get_product API in
https://api.clcplusbackbone.geoville.com/v1/.

The code runs within a docker container. The code mainly consists of commands from the storage gate module.