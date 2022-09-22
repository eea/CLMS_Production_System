########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create region of interest API call
#
# Date created: 10.06.2020
# Date last modified: 17.08.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.08
#
########################################################################################################################

import logging
import threading
from datetime import datetime
from collections import namedtuple
from geoville_ms_receiver.basereceiver import *
from logging_save_config.get_configuration_from_database import *

########################################################################################################################
# Environment variables which are required to read configuration data
########################################################################################################################

os_var_list = [
    'LOGGER_QUEUE_NAME',
    'DATABASE_CONFIG_FILE',
    'DATABASE_CONFIG_FILE_SECTION',
    'RABBIT_MQ_USER',
    'RABBIT_MQ_PASSWORD',
    'RABBIT_MQ_VHOST',
    'LOG_DIR'
]

exited_global = False                   # This variable is set to True when the program is interrupted with CTRL+C
insert_statement_values_global = []     # List which stores the log data tuple in a global way

########################################################################################################################
# Configure the python logger
########################################################################################################################

log_dir = os.environ['LOG_DIR']
log_file = os.path.join(log_dir, 'logging_saver.log')
logging.basicConfig(filename=log_file, level='INFO', format='[ %(asctime)s - %(levelname)s - %(filename)s: %(message)s ]')


########################################################################################################################
# Entry point for the status manager script
########################################################################################################################

class Receiver(BaseReceiver):
    """
    BaseReceiver must be implemented to receive Data from RabbitMQ
    """
    def __init__(self, service):
        super().__init__(service)

    def callback(self, ch, method, properties, body):
        """
        This method is called when queue receives a new message. (Reads the dictionaries from the queue.)
        """
        message = super().callback(ch, method, properties, body)

        if not "orderID" in message.keys():
            message["orderID"] = None

        log_msg = namedtuple("LogMsg", message.keys())(*message.values())
        log_time_obj = datetime.strptime(log_msg.logTime, '%Y-%m-%d %H:%M:%S.%f')

        log_msg_tuple = (log_msg.orderID, log_msg.serviceName, log_msg.logLevel, log_msg.logMessage, log_time_obj)

        insert_statement_values_global.append(log_msg_tuple)


########################################################################################################################
# Entry point for the status manager script
########################################################################################################################

def __store_messages_to_database(insert_parameters, db_config_file, db_config_section, autocommit):
    """
    This function reads the log messages from a global list and sends the data to the database.

    Arguments:
        :param insert_parameters: Global list object which stores the log data which was read from the queue
        :param db_config_file: The filename to the database.ini file
        :param db_config_section: The section in the database.ini file which stores the actual configuration parameters
        :param autocommit: True...ON, False...Off
    """
    if len(insert_parameters) == 0:
        return

    sql = "INSERT INTO logging.logging (order_id, service_name, log_level, log_message, time_stamp) values %s"
    try:
        execute_values_database(sql, insert_parameters, db_config_file, db_config_section, autocommit)
    except Exception as e:
        logging.error("DB_STORE_ERROR: Cannot store message into database - details: {0}".format(str(e)))

    logging.info("DB_STORE_COUNT: Stored {0} messages to database".format(len(insert_parameters)))


########################################################################################################################
# Method definition for validating the environment variables list
########################################################################################################################

def __validate_os_variables(env_var):
    """
    This method checks if all the required environment variables are available in order to run the save module. In case
    of an error, the method throws an exception if one of the required variables is missing.

    Arguments:
        env_var (str): names of the environment variable

    """

    if env_var not in os.environ:
        err_msg = "environment variable {0} is not defined".format(env_var)
        logging.error(err_msg)
        raise Exception(err_msg)


########################################################################################################################
# Method definition for writing log data to the database in a separate thread
########################################################################################################################

def __save_method(db_config_file, db_config_section, autocommit, duration):
    """ Writes log data to the database in a separate thread

    This method is used to start a thread which periodically calls the method which sends the data to the database. A
    separate thread is required because the receiver module already runs in a loop.

    Arguments:
        db_config_file (str): filename to the database.ini file
        db_config_section (str): section in the database.ini file which stores the actual connection parameters
        autocommit (bool): True...ON, False...Off
        duration (int): controls how often (in seconds) the data is written to the database.

    """

    logging.info('Saver thread started')
    start = time.time()

    while True:

        time.sleep(0.2)
        end = time.time()
        elapsed = end - start

        if elapsed >= float(duration):
            global insert_statement_values_global

            # Persist the messages
            local_insert_statement_list = list(insert_statement_values_global)
            insert_statement_values_global = []
            __store_messages_to_database(local_insert_statement_list, db_config_file, db_config_section, autocommit)

            # Heartbeat
            logging.info("DB_STORE_STATUS: Saver thread")
            start = time.time()

        if exited_global:
            logging.info('Saver thread exited')
            break


########################################################################################################################
# Method definition for creating the log file directory
########################################################################################################################

def create_log_file(local_log_dir):
    """ Creates a log file directory

    This method create the directory where the local log messages are stored, derived from this module. If the directory
    already exist, an existing file will be used.

    Arguments:
        local_log_dir (str): name of the directory

    """

    if not os.path.exists(local_log_dir):
        os.mkdir(local_log_dir)


########################################################################################################################
# Entry point for the logger saver module script
########################################################################################################################

if __name__ == '__main__':

    logging.info("Logging saver started")

    # Validate os variables
    list(map(__validate_os_variables, os_var_list))

    logger_queue_name = os.environ['LOGGER_QUEUE_NAME']
    db_config_file = os.environ['DATABASE_CONFIG_FILE']
    db_config_section = os.environ['DATABASE_CONFIG_FILE_SECTION']

    # Create log file
    create_log_file(log_dir)

    configuration = get_logger_saver_configuration(db_config_file, db_config_section)
    duration = configuration.duration
    autocommit = True

    saver_thread = threading.Thread(target=__save_method,
                                    args=(db_config_file, db_config_section, autocommit, duration))
    saver_thread.start()

    try:
        logging.info('Start RabbitMQ receiver')
        receiver = Receiver(logger_queue_name)
        receiver.listen()
    except Exception as e:
        exited_global = True
        logging.error('RabbitMQ receiver exited with an error: ', str(e))

    logging.info('RabbitMQ receiver exited')
    exited_global = True
