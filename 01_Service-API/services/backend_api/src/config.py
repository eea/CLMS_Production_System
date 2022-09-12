########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# API Gateway config file
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from lib.database_helper import get_database_connection_str
import os


########################################################################################################################
# General configuration class
########################################################################################################################

class Config(object):

    DEBUG = False
    TESTING = False
    DATABASE_CONFIG_FILE = os.environ.get('DATABASE_CONFIG_FILE')
    DATABASE_CONFIG_FILE_SECTION_API = os.environ.get('DATABASE_CONFIG_FILE_SECTION')
    DATABASE_CONFIG_FILE_SECTION_OAUTH = os.environ.get('DATABASE_CONFIG_FILE_SECTION_OAUTH')

    BUNDLE_ERRORS = True

    RESTX_MASK_SWAGGER = False
    RESTX_INCLUDE_ALL_MODELS = False

    RABBIT_MQ_HOST = os.environ.get('RABBIT_MQ_HOST')
    RABBIT_MQ_USER = os.environ.get('RABBIT_MQ_USER')
    RABBIT_MQ_PASSWORD = os.environ.get('RABBIT_MQ_PASSWORD')
    RABBIT_MQ_MANAGEMENT_PORT = os.environ.get('RABBIT_MQ_MANAGEMENT_PORT')
    RABBIT_MQ_VIRTUAL_HOST = os.environ.get('RABBIT_MQ_VHOST')

    SCOPE_CONNECTOR = 'OR'

    OAUTH_USER = os.environ.get('OAUTH2_USER')
    OAUTH_PASSWORD = os.environ.get('OAUTH2_PASSWORD')
    OAUTH_CREATE_CLIENT_ADDRESS = os.environ.get('OAUTH2_SERVER_BASE_URL') + '/oauth/create_client'
    OAUTH_GENERATE_TOKEN_ADDRESS = os.environ.get('OAUTH2_SERVER_BASE_URL') + '/oauth/generate_token'
    OAUTH_VALIDATE_TOKEN_ADDRESS = os.environ.get('OAUTH2_SERVER_BASE_URL') + '/oauth/validate_token'
    OAUTH_REVOKE_TOKEN_ADDRESS = os.environ.get('OAUTH2_SERVER_BASE_URL') + '/oauth/revoke_token'
    OAUTH2_TOKEN_EXPIRES_IN = {
        'password': os.environ.get('BEARER_TOKEN_EXPIRATION_TIME'),
        'refresh_token': os.environ.get('REFRESH_TOKEN_EXPIRATION_TIME'),
    }


########################################################################################################################
# Production configuration
########################################################################################################################

class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = get_database_connection_str(Config.DATABASE_CONFIG_FILE,
                                                          Config.DATABASE_CONFIG_FILE_SECTION_OAUTH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


########################################################################################################################
# Development configuration
########################################################################################################################

class DevelopmentConfig(Config):

    DEBUG = True
    PORT = 5001
    HOST = '0.0.0.0'

    SQLALCHEMY_DATABASE_URI = get_database_connection_str(Config.DATABASE_CONFIG_FILE,
                                                          Config.DATABASE_CONFIG_FILE_SECTION_OAUTH)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
