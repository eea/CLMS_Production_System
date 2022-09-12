"""
The filereader for a config file

Author:
Wolfgang Kapferer
date:2019-07-08
Version v0.1
"""
# !/usr/bin/env python3

from configparser import ConfigParser


def config_postgresql(filename, section) -> object:
    """
    :param filename: Name of the config file providing the credentials for the database connection
    :param section: the section in the database credential file providing us
    :return parameters from the configuration section
    ---------------------------------------
    A typical database config file example:
    [sectionName]
    host=xxxxx
    database=xxxxx
    user= xxxxx
    password=xxxxx
    ---------------------------------------
    :return: a list with all necessary information to establish a database connection
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    section_data = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            section_data[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return section_data
