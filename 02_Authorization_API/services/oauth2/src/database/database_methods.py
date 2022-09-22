########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Methods for database connection establishment
#
# Date created: 08.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from configparser import ConfigParser


########################################################################################################################
# Retrieving configuration parameters from section of the database_development.ini file
########################################################################################################################

def get_config_section_data(filename, section):
    """ Returns the all section of parameter of an INI file

    This method returns

    Arguments:
        filename (str): Name of the config file providing the credentials for the database connection
        section (str): the section in the database.ini file

    Returns:
        parameters (dict): dict of configuration parameters

    """

    parser = ConfigParser()
    parser.read(filename)

    section_data = {}
    if parser.has_section(section):
        params = parser.items(section)

        for param in params:
            section_data[param[0]] = param[1]

    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return section_data


########################################################################################################################
# Creates a database connection string for SQLAlchemy
########################################################################################################################

def get_database_connection_str(database_ini_file, database_config_section):
    """ Creates a database connection string

    This method creates a database connection string for a SQLAlchemy
    database object. It retrieves the values from a database configuration
    file which contains several sections.

    Arguments:
        database_ini_file (str): database_development.ini file
        database_config_section (str): section of the database.ini file

    Returns:
        (str): the database connection string

    """

    db_params = get_config_section_data(database_ini_file, database_config_section)
    return f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}'