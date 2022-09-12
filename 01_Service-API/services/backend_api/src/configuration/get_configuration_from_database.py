import re
from configuration.configuration import Configuration
from geoville_ms_database.geoville_ms_database import *


def __get_message_key_from_database(databaseconfigfile, databaseconfigsection):
    """
    Extracts the message key from the database
    :param databaseconfigfile: the file path and name for the database.ini file
    :param databaseconfigsection: the section in the database.ini file for postgresql
    :return: a dictionary holding the key
    """
    sql = "SELECT \"name\", \"key\" FROM msgeovilleconfig.message_key"
    result = read_from_database_one_row(sql, None, databaseconfigfile, databaseconfigsection, False)
    key_store = {result[0]: result[1]}

    return key_store


def __get_message_queue_config_from_database(servicename, databaseconfigfile, databaseconfigsection):
    """
    Extracts the queue configuration for a given servicename
    :param servicename: the servicename
    :param databaseconfigfile: the file path and name for the database.ini file
    :param databaseconfigsection: the section in the database.ini file for postgresql
    :return: a dictionary holding the queue configuration
    """
    sql = "SELECT  \"key\", \"value\" FROM msgeovilleconfig.message_queue_config " \
          "where queue_name = '" + servicename + "'"
    result = read_from_database_all_rows(sql, None, databaseconfigfile, databaseconfigsection, False)

    config = __get_dictionary_from_result(result)

    return config


def __get_dictionary_from_result(result):
    """
    returns a dictionary from a database result tuple
    :param result:
    :return: dictionary
    """
    dictionary = {}
    for x, y in result:
        if dictionary.keys() == x:
            dictionary[y].append(y)
        else:
            dictionary[x] = [y]

    return dictionary


def get_queue_configuration(service, databaseconfigfile, databaseconfigsection):
    """
    The public method to get the service configuration
    :param service: servicename
    :param databaseconfigfile: the file path and name for the database.ini file
    :param databaseconfigsection: the section in the database.ini file for postgresql
    :return: an object holding all necessary configuration information for rabbitMQ
    """
    key = __get_message_key_from_database(databaseconfigfile, databaseconfigsection)
    message_queue_config = __get_message_queue_config_from_database(service, databaseconfigfile, databaseconfigsection)

    host = message_queue_config.get("host")
    port = str(message_queue_config.get("port"))
    port_int = [int(port) for port in re.findall('\\d+', port)]

    api_configuration = Configuration(host[0], port_int[0], service, key.get("message_key"))

    return api_configuration
