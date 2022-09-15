"""
The test file for testing the geoville_ms_database module
only Postgres is supported at the moment

Author:
Wolfgang Kapferer
date:2019-07-08
Version v0.1
"""
from geoville_ms_database.geoville_ms_database import *
import unittest


def read_one_row_test(sql, values):
    """
    Method for testing Read one Row
    :param sql: the query
    :param values: the values
    :return: A Result Tuple
    """
    print("Test for Select")
    result = read_from_database_one_row(sql, values, 'database.ini', 'postgresql', False)
    return result


def read_all_test(sql, values):
    """
    Method for reading all rows from a query
    :param sql: the query
    :param values: the values
    :return: A Result Tuple
    """
    print("Test for read all")
    result = read_from_database_all_rows(sql, values, 'database.ini', 'postgresql', False)
    return result


def read_many_test(sql, values, size):
    """
    Method for reading amy (size) rows from a query
    :param sql: the query
    :param values: the values
    :param size
    :return: A Result Tuple
    """
    print("Test for select many")
    result = read_from_database_many_rows(sql, values, size, 'database.ini', 'postgresql', False)
    return result


def execute_test(sql, values):
    """
    Method to execute a DB-Command (create, update, insert, etc.)
    :param sql: the query
    :param values: the values
    :return: success
    """
    print("Test execute")
    success = execute_database(sql, values, 'database.ini', 'postgresql', False)
    return success


def execute_values_test(sql, parameter_list):
    """
    Method to execute many row insert, update, delete
    :param sql: the query
    :param parameter_list: the list with the data
    :return: success
    """
    print("Test for many inserts/updates/etc.")
    success = execute_values_database(sql, parameter_list, 'database.ini', 'postgresql', False)
    return success


class TestOneRowRead(unittest.TestCase):
    """
    The class for reading one row
    """
    def test(self):
        sql = "SELECT 'readable'"
        self.assertEqual(read_one_row_test(sql, None)[0], 'readable')


class TestAllRowsRead(unittest.TestCase):
    """
    Test class for fetch all
    """
    def test(self):
        sql = "SELECT generate_series(1,10)"
        self.assertEqual(read_all_test(sql, None), [(1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,), (10,)])


class TestManyRowsRead(unittest.TestCase):
    """
    Test class for reading many (size) Rows
    """
    def test(self):
        sql = "SELECT generate_series(1,10)"
        self.assertEqual(read_many_test(sql, None, 2), [(1,), (2,)])


class TestInsert(unittest.TestCase):
    """
    Test class for inserting one table
    """
    def test(self):
        sql = "drop table if exists public.test"
        self.assertEqual(execute_test(sql, None), True)

        sql = "create table public.test(spalte varchar(100))"
        self.assertEqual(execute_test(sql, None), True)

        sql = "INSERT INTO public.test (spalte) VALUES('TESTWERT')"
        self.assertEqual(execute_test(sql, None), True)

        sql = "drop table public.test"
        self.assertEqual(execute_test(sql, None), True)


class TestBatchWork(unittest.TestCase):
    """
    Test for execute many
    """
    def test(self):
        sql = "drop table if exists public.test"
        self.assertEqual(execute_test(sql, None), True)

        sql = "create table public.test(spalte varchar(100))"
        self.assertEqual(execute_test(sql, None), True)

        value_list = [(i,) for i in range(10)]

        sql = "INSERT INTO public.test (spalte) values %s"
        self.assertEqual(execute_values_test(sql, value_list), True)

        sql = "drop table public.test"
        self.assertEqual(execute_test(sql, None), True)
