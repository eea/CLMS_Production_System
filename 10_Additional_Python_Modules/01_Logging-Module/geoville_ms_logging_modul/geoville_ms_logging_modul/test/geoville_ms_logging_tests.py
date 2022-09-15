"""
The test file for testing the geoville_ms_logging_module.

Author: Patrick Wolf
Date: 2019-10-01
Version 19.10.1
"""

import unittest
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
import random
import time


class TestLogMessageInfo(unittest.TestCase):
    """
    Test class for storing a INFO message
    """
    def test(self):
        self.assertEqual(log("seasonality", LogLevel.INFO, "This is a test INFO message"), True)


class TestLogMessageDebug(unittest.TestCase):
    """
    Test class for storing a DEBUG message
    """
    def test(self):
        self.assertEqual(log("seasonality", LogLevel.DEBUG, "This is a test DEBUG message"), True)


class TestLogMessageWarning(unittest.TestCase):
    """
    Test class for storing a WARNING message
    """
    def test(self):
        self.assertEqual(log("seasonality", LogLevel.WARNING, "This is a test WARNING message"), True)


class TestLogMessageError(unittest.TestCase):
    """
    Test class for storing a ERROR message
    """
    def test(self):
        self.assertEqual(log("seasonality", LogLevel.ERROR, "This is a test ERROR message"), True)


class TestLogMultipleMessages(unittest.TestCase):
    """
    Test class for storing multiple log messages
    """
    def test(self):
        for i in range(10):
            time.sleep(random.uniform(0.01, 0.05))
            my_str = "This is a test INFO message - {0}".format(str(i))
            self.assertEqual(log("seasonality", LogLevel.INFO, my_str), True)


class TestLogMessageIncorrectLogLevel(unittest.TestCase):
    """"
    Test class for using an incorrect log level type
    """
    def test(self):
        with self.assertRaises(TypeError):
            self.assertEqual(log("seasonality", "incorrect_log_level", "This is a test INFO message"), False)
