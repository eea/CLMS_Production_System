########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Retrieves the entire message queue configuration from the database
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import config_namespace as api
from lib.auth_header import auth_header_parser
from models.models_config.queue_config.queue_config_models import queue_config_list_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the get message queue configuration API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetMessageQueueConfig(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get message queue configuration script. The class consists of one method
    which accepts a GET request. For the GET request no additional parameters are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation successful', queue_config_list_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving the message queue configuration

        <p style="text-align: justify">This method defines the handler for the GET request of the get message queue
        configuration script. It returns a message wrapped in a dictionary with the configuration from the database.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        try:
            db_query = """SELECT 
                              service_id, queue_name, host, port
                          FROM 
                              msgeovilleconfig.message_queue_config
                       """

            conf_data = read_from_database_all_rows(db_query, (), database_config_file, database_config_section_api, True)

            res_array = []

            for config in conf_data:
                config_obj = {
                    'service_id': config[0],
                    'queue_name': config[1],
                    'host': config[2],
                    'port': config[3]
                }

                res_array.append(config_obj)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-get_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-get_queue_config', LogLevel.INFO, f'Request successful')
            return {'message_queue_configuration': res_array}, 200
