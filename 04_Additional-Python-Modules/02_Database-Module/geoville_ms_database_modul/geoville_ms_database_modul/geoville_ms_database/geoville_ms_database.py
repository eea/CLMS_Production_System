"""
The geoville_ms_database module
only Postgres is supported at the moment

Author:
Wolfgang Kapferer
date:2019-08-13
Version 19.08.2
"""

from database import postgresql


def read_from_database_one_row(sql, values, filename, section, autocommit):
    """
    This function is nice to read just one row
    :param sql: The string providing the query
    :param values: The values for the query
    :param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: A tuple with ONE item with the result
    """
    connection = __connect_to_database(filename, section, autocommit)
    result = postgresql.__query_select_fetch_one_row(connection, sql, values)
    __close_database_connection(connection)

    return result


def read_from_database_all_rows(sql, values, filename, section, autocommit):
    """
    This function is nice to read more data
    :param sql: The string providing the query
    :param values: The values for the query
    :param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: A tuple holding all the data
    """
    connection = __connect_to_database(filename, section, autocommit)
    result = postgresql.__query_select_fetchall(connection, sql, values)
    __close_database_connection(connection)

    return result


def read_from_database_many_rows(sql, values, size, filename, section, autocommit):
    """
    This function is nice to read more data
    :param sql: The string providing the query
    :param values: The values for the query
    :param size: How many rows should be returned
    :param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: A tuple holding all the data
    """
    connection = __connect_to_database(filename, section, autocommit)
    result = postgresql.__query_select_fetchmany(connection, sql, values, size)
    __close_database_connection(connection)

    return result


def execute_database(sql, values, filename, section, autocommit):
    """
    This function executes a command against the DB
    :param sql: The string providing the query
    :param values: The values for the query
    :param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: success
    """
    connection = __connect_to_database(filename, section, autocommit)
    success = postgresql.__execute_database(connection, sql, values)
    __close_database_connection(connection)

    return success


def execute_values_database(sql, param_list, filename, section, autocommit):
    """
    This function execute many onto the database (for updates, inserts, del operations)
    :param sql: The string providing the query
    :param param_list: The list to execute values
    :param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: success
    """
    connection = __connect_to_database(filename, section, autocommit)
    success = postgresql.__execute_values(connection, sql, param_list)
    __close_database_connection(connection)

    return success


def __connect_to_database(filename, section, autocommit):
    """
    Connect to the database
    param filename: The Filename to the database.ini file
    :param section: The section in the credentials files
    :param autocommit: True...ON, False...Off
    :return: the database connection
    """
    params = postgresql.__read_credentials(filename, section)
    connection = postgresql.__connect_to_database(params, autocommit)
    connection.commit()

    return connection


def __close_database_connection(connection):
    """
    Close the database connection
    :param connection:
    :return: success
    """
    success = postgresql.__close_connection(connection)

    return success
