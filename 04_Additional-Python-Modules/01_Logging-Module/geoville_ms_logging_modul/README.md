# GeoVille_MS_Logger_Module

This section summarizes the logging module (GeoVille_MS_Logger_Modul) and shows how to install and use the logging module.

- Author: Wolf Patrick / Johannes Schmid
- Version 20.07.01
- Date: 2020-07-08

## Introduction

The logging module is used to send log message (in form of a dictionary) to a logging queue. Please note that the
environment variables listed below are required:

- LOGGER_QUEUE_NAME: Addresses the configuration parameter fields for the logger queue in the database
- DATABASE_CONFIG_FILE: The filename to the database.ini file
- DATABASE_CONFIG_FILE_SECTION: The section in the database.ini file which stores the actual database connection information
- RABBIT_MQ_USER: RabbitMQ username
- RABBIT_MQ_PASSWORD: RabbitMQ username
- RABBIT_MQ_VHOST: RabbitMQ virtual host

Optional environment variables (see documentation for details):

- SERVICE_NAME: Service which sends the logging information
- ORDER_ID: ID of the order / service that gets logged 

## Short overview of all public methods

The logging module provides a public method to publish log messages to a RabbitMq queue:

- _log(service_name, log_level, log_message, order_id=None)_ (**deprecated**)
- _gemslog(log_level, log_message, service_name=None, order_id=None)_:

## Log-level

The logger module supports different log levels. The log-level must be a valid LogLevel enumeration member. The supported
levels, in order of increasing severity, are the following:

- INFO: Confirmation that things are working as expected
- WARNING: Indicates that something unexpected happened. The software is still working as expected
- ERROR: Indicates a serious problem. The software has not been able to perform some function

## Example calls

#### log(service_name, log_level, log_message, order_id=None)

*The function log is deprecated. Please use the function gemslog*

This function sends a log message (log dictionary) to the message queue. The logging information  (consisting of:
service name, log level, actual message, order id and time information) is stored in a dictionary. This dictionary
is published to the logger queue by applying functionality of the geoville_ms_publisher module. Please note that the
time stamp is set automatically. 

If the argument *order_id* is *None*, the function reads the order id from the
environment variable **ORDER_ID**. IMPORTANT: This function supports missing order ids.
```
:param service_name: Name of the service which sends the log message
:param log_level: Log-level of the message - must be a valid LogLevel enumeration member
:param log_message: Actual content of the log message as sting
:param order_id: ID of the order that gets logged. (Default: None; Envoronment variable: ORDER_ID) [type: string]
:return: True if the message was sent successfully to the logging queue, False otherwise
```

#### gemslog(log_level, log_message, service_name=None, order_id=None)

This function sends a log message (log dictionary) to the message queue. The logging information  (consisting of:
log level, actual message, service name, order id and time information) is stored in a dictionary. This dictionary
is published to the logger queue by applying functionality of the geoville_ms_publisher module. Please note that the
time stamp is set automatically. 

If the argument *service_name* is *None*, the function reads the service name from the environment variable 
**SERVICE_NAME**. IMPORTANT: The service name information is mandatory and can not be *None*. 

If the argument *order_id* is *None*, the function reads the order id from the environment variable **ORDER_ID**. 
IMPORTANT: This function supports missing order ids.
```
:param log_level: Log-level of the message - must be a valid LogLevel enumeration member
:param log_message: Actual content of the log message as sting
:param service_name: Name of the service which sends the log message. (Default: None; Envoronment variable: SERVICE_NAME) 
:param order_id: ID of the order that gets logged. (Default: None; Envoronment variable: ORDER_ID) [type: string]
:return: True if the message was sent successfully to the logging queue, False otherwise
```

## Tests

The tests can be found in the subdirectory test.

## Installation & usage

Please install the module with the pip3 installer and import it afterwards.

**Installation**

The module can be installed by applying the pip3 install command.

E.g.: pip3 install https://${GIT_USER}:${GIT_PW}@bitbucket.org/geoville/geoville_ms_logging_modul/get/master.zip --user

Please check if the environment variables _GIT_USER_ and _GIT_PW_ are available.

**Dependencies**

- [GeoVille_MS_RabbitMQ_Modul](https://bitbucket.org/geoville/geoville_ms_rabbitmq_modul/src/master/)

**Usage**

After installing the module, it can be imported. Please see the example below:
```
from geoville_ms_logging.geoville_ms_logging import *

# Log messag without order id
log("seasonality", LogLevel.INFO, "This is a test INFO message")

# Log messag with order id
log("seasonality", LogLevel.INFO, "This is a test INFO message with an order is", order_id=123456)


# Log messag without service name information -> Reads the service name from the environment variable SERVICE_NAME
gemslog(LogLevel.INFO, "This is another message", order_id=12345)

# Log messag without order id information -> Reads the order id from the environment variable ORDER_ID
gemslog(LogLevel.INFO, This is another message", service_name="seasonaliy")

# Reads service name and order id from envoronment variables
gemslog(LogLevel.INFO, This is yet another message")
```

