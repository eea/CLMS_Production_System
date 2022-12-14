########################################################################################################################
#
# Initialising environment variables
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from init.app_constructor import app

########################################################################################################################
# RabbitMQ environment variables
########################################################################################################################

rabbitmq_host = app.config['RABBIT_MQ_HOST']
rabbitmq_user = app.config['RABBIT_MQ_USER']
rabbitmq_password = app.config['RABBIT_MQ_PASSWORD']
rabbitmq_management_port = app.config['RABBIT_MQ_MANAGEMENT_PORT']
rabbitmq_virtual_host = app.config['RABBIT_MQ_VIRTUAL_HOST']

########################################################################################################################
# Database environment variables
########################################################################################################################

database_config_file = app.config['DATABASE_CONFIG_FILE']
database_config_section_api = app.config['DATABASE_CONFIG_FILE_SECTION_API']
database_config_section_oauth = app.config['DATABASE_CONFIG_FILE_SECTION_OAUTH']

########################################################################################################################
# OAuth2 environment variables
########################################################################################################################

oauth2_create_client = app.config['OAUTH_CREATE_CLIENT_ADDRESS']
oauth2_generate_token = app.config['OAUTH_GENERATE_TOKEN_ADDRESS']
oauth2_validate_token = app.config['OAUTH_VALIDATE_TOKEN_ADDRESS']
oauth2_revoke_token = app.config['OAUTH_REVOKE_TOKEN_ADDRESS']
oauth2_user = app.config['OAUTH_USER']
oauth2_password = app.config['OAUTH_PASSWORD']
oauth2_bearer_expiration_time = app.config['OAUTH2_TOKEN_EXPIRES_IN']['password']
oauth2_refresh_expiration_time = app.config['OAUTH2_TOKEN_EXPIRES_IN']['refresh_token']
