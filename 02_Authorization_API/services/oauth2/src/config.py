########################################################################################################################
#
# API Gateway config file
#
# Date created: 21.10.2019
# Date last modified: 29.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from database.database_methods import get_database_connection_str
import os


########################################################################################################################
# General configuration class
########################################################################################################################

class Config(object):

    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    OAUTH2_TOKEN_EXPIRES_IN = {
        'password': os.environ.get('BEARER_TOKEN_EXPIRATION_TIME'),
        'refresh_token': os.environ.get('REFRESH_TOKEN_EXPIRATION_TIME'),
    }
    DATABASE_CONFIG_FILE = os.environ.get('DATABASE_CONFIG_FILE')
    DATABASE_CONFIG_FILE_SECTION = os.environ.get('DATABASE_CONFIG_FILE_SECTION')
    SQLALCHEMY_DATABASE_URI = get_database_connection_str(DATABASE_CONFIG_FILE, DATABASE_CONFIG_FILE_SECTION)


########################################################################################################################
# Production configuration class
########################################################################################################################

class ProductionConfig(Config):

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


########################################################################################################################
# Development configuration class
########################################################################################################################

class DevelopmentConfig(Config):

    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
