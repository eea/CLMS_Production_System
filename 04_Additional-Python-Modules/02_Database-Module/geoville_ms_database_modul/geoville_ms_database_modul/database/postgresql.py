"""
The postgresql geoville_ms  module
only Postgres is supported at the moment

Author:
Wolfgang Kapferer
date:2019-07-08
Version v0.1
"""
# !/usr/bin/env python3
import psycopg2
import psycopg2.extras
from database.local_config import config_postgresql


def __read_credentials(filename, section):
    """
    Read the DB credentials from a given vonfig file
    :param filename: the path and filename to the system configuration file
    :param section:
    :return: the parameters
    """
    params = config_postgresql(filename, section)

    return params


def __connect_to_database(params, autocommit):
    """
    The method to connect to the database
    :param params: the params from the configuration file
    :param autocommit: True...on, False...off
    :return: an active connection
    """
    print('Connecting to the PostgreSQL database...')
    connection = None
    try:
        connection = psycopg2.connect(**params)
        connection.set_session(autocommit=autocommit)
        connection.commit()
    except psycopg2.OperationalError as error:
        print('Unable to connect! Error: {}'.format(error))
    else:
        print('connection established')

    return connection


def __query_select_fetch_one_row(connection, query, values):
    """
    The fetchone row method
    :param connection: active connection to the DB
    :param query: the Query-SQL
    :param values: the values for the query
    :return: the result tuple
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()
        connection.commit()
    except psycopg2.OperationalError as error:
        print('error fetchone querySelect "{}", error: {}'.format(query, error))
        return False
    else:
        return result


def __query_select_fetchall(connection, query, values):
    """
    The fetchall row method
    :param connection: active connection to the DB
    :param query: the Query-SQL
    :param values: the values for the query
    :return: the result tuple
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchall()
        connection.commit()
    except psycopg2.OperationalError as error:
        print('error fetchall querySelect "{}", error: {}'.format(query, error))
        return False
    else:
        return result


def __query_select_fetchmany(connection, query, values, rows):
    """
    The fetchmany row method
    :param connection: active connection to the DB
    :param query: the Query-SQL
    :param values: the values for the query
    :param rows: how many rows to return
    :return: the result tuple
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchmany(rows)
        connection.commit()
    except psycopg2.OperationalError as error:
        print('error fetchmany querySelect "{}", error: {}'.format(query, error))
        return False
    else:
        return result


def __execute_database(connection, command, values):
    """
    The execute a command in the DB method
    :param connection: active connection to the DB
    :param command: the command
    :param values: the values for the query
    :return: success
    """
    try:
        cursor = connection.cursor()
        cursor.execute(command, values)
        connection.commit()
    except psycopg2.OperationalError as error:
        print('error execute sql "{}", error: {}'.format(command, error))
        return False
    else:
        return True


def __execute_values(connection, query, param_list):
    """
    The execute many values command, for large updates, large inserts, etc.
    :param connection:
    :param query:
    :param param_list:
    :return: success
    """
    try:
        cursor = connection.cursor()
        psycopg2.extras.execute_values(cursor, query, param_list)
        connection.commit()
    except psycopg2.OperationalError as error:
        print('error in execute_batch "{}", error: {}'.format(query, error))
        return False
    else:
        return True


def __close_connection(connection):
    """
    Close the connection
    :param connection:
    :return: success
    """
    try:
        connection.close()
    except psycopg2.OperationalError as error:
        print('error closing connection {}'.format(error))
        return False
    else:
        print('connection closed')
        return True


def __del__(connection):
    """
    Destructor for the connection
    :param connection:
    """
    connection.close()
