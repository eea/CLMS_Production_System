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

from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from logging_save_config.configuration import Configuration
import re


########################################################################################################################
# Method definition for the extraction of the logging configuration
########################################################################################################################

def __get_logger_saver_config_from_database(database_configfile, database_config_section):
    """ Retrieves logging configuration from the database

    This method extracts all the configuration parameters for the logging service from the database and returns it

    Arguments:
        database_configfile (str): the file path and name for the database.ini file
        database_config_section (str): the section in the database.ini file for postgresql

    Returns:
        (dict): holding the configuration parameter

    """

    sql = "SELECT * FROM msgeovilleconfig.logger_saver_config"
    result = read_from_database_all_rows(sql, None, database_configfile, database_config_section, False)
    return __get_dictionary_from_result(result)


########################################################################################################################
# Method definition for creating a dictionary from a database query result
########################################################################################################################

def __get_dictionary_from_result(result):
    """ Converts the result of a database query into a dictionary

    This method takes as input a database query result in form of a tuple and returns a dictionary for further
    processing the queried data.

    Arguments:
        result (tuple): database query result

    Returns:
        (dict): database query result in form of a dictionary

    """

    dictionary = {}

    for x, y in result:
        if dictionary.keys() == x:
            dictionary[y].append(y)
        else:
            dictionary[x] = [y]

    return dictionary


########################################################################################################################
# Method definition for retrieving the logger saver configuration
########################################################################################################################

def get_logger_saver_configuration(database_configfile, database_config_section):
    """ Retrieves the logger saver configuration

    This public method retrieving the logger saver configuration parameters for the saver and returns it in form of an
    configuration object

    Arguments:
        database_configfile (str): the file path and name for the database.ini file
        database_config_section (str): the section in the database.ini file for postgresql

    Returns:
        (obj): holding all necessary configuration information for the log saver

    """

    log_saver_config = __get_logger_saver_config_from_database(database_configfile, database_config_section)

    duration = str(log_saver_config.get("duration_in_sec"))
    duration_int = [int(duration) for duration in re.findall('\\d+', duration)][0]  # match one or more digits

    api_configuration = Configuration(duration_int)

    return api_configuration
