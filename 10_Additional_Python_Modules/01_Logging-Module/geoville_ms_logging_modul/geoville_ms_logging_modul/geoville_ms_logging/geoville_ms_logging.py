#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The geoville_ms_logging module sends a log message (in the form of a dictionary) to the logging queue.

Please note that the environment variable listed below are required:

    - LOGGER_QUEUE_NAME: Addresses the configuration parameter fields in the database
    - DATABASE_CONFIG_FILE: The filename to the database.ini file
    - DATABASE_CONFIG_FILE_SECTION: The section in the database.ini file which stores the actual database connection information
    - RABBIT_MQ_USER: RabbitMQ username
    - RABBIT_MQ_PASSWORD: RabbitMQ username
    - RABBIT_MQ_VHOST: RabbitMQ virtual host

Dependencies: For publishing a message, the geoville_ms_publisher (GeoVille_MS_Database_Module) is required.

Author: Wolf Patrick
Date: 2019-10-01
Version 19.10.1
"""

import os
from enum import Enum
import logging
import warnings
from datetime import datetime
from geoville_ms_publisher.publisher import Publisher


# Configure the logger
logging.basicConfig(level='INFO', format='[ %(asctime)s - %(levelname)s - %(filename)s: %(message)s ]')

# Environment variables which are required to read configuration data
os_var_list = [
    'LOGGER_QUEUE_NAME',
    'DATABASE_CONFIG_FILE',
    'DATABASE_CONFIG_FILE_SECTION',
    'RABBIT_MQ_USER',
    'RABBIT_MQ_PASSWORD',
    'RABBIT_MQ_VHOST',
]


class LogLevel(Enum):
    """
    This class is used to define the log leg-level. The supported levels, in order of increasing severity, are the following:
    INFO: Confirmation that things are working as expected
    WARNING: Indicates that something unexpected happened. The software is still working as expected
    ERROR: Indicates a serious problem. The software has not been able to perform some function
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


def __validate_os_variables(env_var):
    """
    This function checks if all environment variables are available which are required to read the configuration data.
    The function throws an exception if one of the required variables is missing.
    :param env_var: The name of the environment variable
    """
    if env_var not in os.environ:
        print(env_var)
        err_msg = "environment variable {0} is not defined".format(env_var)
        logging.error(err_msg)
        raise Exception(err_msg)


def log(service_name, log_level, log_message, order_id=None):
    """
    This function sends a log message (log dictionary) to the message queue. The logging information  (consisting of:
    service name, log level, actual message, order id and time information) is stored in a dictionary. This dictionary
    is published to the logger queue by applying functionality of the geoville_ms_publisher module. Please note that the
    time stamp is set automatically.

    If the argument order_id is None, the function reads the order id from the environment variable ORDER_ID.
    IMPORTANT: This function supports missing order ids.

    :param service_name: Name of the service which sends the log message
    :param log_level: Log-level of the message - must be a valid LogLevel enumeration member
    :param log_message: Actual content of the log message as sting
    :param order_id: ID of the order that gets logged. Default: None [type: string]
    :return: True if the message was sent successfully to the logging queue, False otherwise
    """

    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn('The function log is deprecated. Please use the function gemslog.', DeprecationWarning, 2)

    logger_queue = os.environ['LOGGER_QUEUE_NAME']

    # Validate os variables
    list(map(__validate_os_variables, os_var_list))

    # Check if log level is correct
    if not isinstance(log_level, LogLevel):
        logging.error("log_level - {0} - is not supported".format(log_level))
        raise TypeError('log_level must be an instance of LogLevel enum')

    log_time_str = datetime.utcnow().__str__()

    # read order_id from environment variable if not given
    if not order_id:
        order_id = os.getenv("ORDER_ID")

    # Dictionary which stores the actual log information
    log_dict = {
        "orderID": order_id,
        "serviceName": service_name,
        "logLevel": log_level.value,
        "logMessage": log_message,
        "logTime": log_time_str
    }

    # Publish log dictionary
    publisher = Publisher(logger_queue)
    try:
        publisher.publish(log_dict)
        logging.info("message - {0} - was sent to the logger queue".format(log_dict))
    except:
        return False
    else:
        return True


def gemslog(log_level, log_message, service_name=None, order_id=None):
    """
    This function sends a log message (log dictionary) to the message queue. The logging information  (consisting of:
    log level, actual message, service name, order id and time information) is stored in a dictionary. This dictionary
    is published to the logger queue by applying functionality of the geoville_ms_publisher module. Please note that the
    time stamp is set automatically.

    If the argument service_name is None, the function reads the service name from the environment variable  SERVICE_NAME
    IMPORTANT: The service name information is mandatory and can not be None.

    If the argument order_id is None, the function reads the order id from the environment variable ORDER_ID.
    IMPORTANT: This function supports missing order ids.

    :param service_name: Name of the service which sends the log message. Default: None
    :param log_level: Log-level of the message - must be a valid LogLevel enumeration member
    :param log_message: Actual content of the log message as sting.
    :param order_id: ID of the order that gets logged. Default: None. [string]
    :return: True if the message was sent successfully to the logging queue, False otherwise
    """

    logger_queue = os.environ['LOGGER_QUEUE_NAME']

    # Validate os variables
    list(map(__validate_os_variables, os_var_list))

    # Check if log level is correct
    if not isinstance(log_level, LogLevel):
        logging.error("log_level - {0} - is not supported".format(log_level))
        raise TypeError('log_level must be an instance of LogLevel enum')

    log_time_str = datetime.utcnow().__str__()

    # read service_name and order_id from environment variable if not given
    if not order_id:
        order_id = os.getenv("ORDER_ID")

    if not service_name:
        service_name = os.getenv("SERVICE_NAME")

    if not service_name:
        raise Exception("Mandatory argument service_name is missing!")

    # Dictionary which stores the actual log information
    log_dict = {
        "orderID": order_id,
        "serviceName": service_name,
        "logLevel": log_level.value,
        "logMessage": log_message,
        "logTime": log_time_str
    }

    # Publish log dictionary
    publisher = Publisher(logger_queue)
    try:
        publisher.publish(log_dict)
        logging.info("message - {0} - was sent to the logger queue".format(log_dict))
    except:
        return False
    else:
        return True
