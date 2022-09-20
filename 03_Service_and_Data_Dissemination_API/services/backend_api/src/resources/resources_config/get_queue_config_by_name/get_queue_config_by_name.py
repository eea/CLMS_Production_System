########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Retrieves the entire message queue configuration by name from the database
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file as db_file, database_config_section_api as db_section
from init.namespace_constructor import config_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_queue_existence
from models.models_config.queue_config.queue_config_models import add_queue_config_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the get queue configuration by name API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('queue_name', 'Queue_name to be requested')
class GetMessageQueueConfigByName(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get queue configuration by name script. The class consists of one method
    which accepts a GET request. For the GET request no additional parameters are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', add_queue_config_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, queue_name):
        """ GET definition for retrieving the message queue configuration by name

        <p style="text-align: justify">This method defines the handler for the GET request of the get queue
        configuration by name script. It returns a message wrapped in a dictionary with the configuration from the
        database.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Path parameters:</b>
        <ul>
        <li><p><i>service_name (str): </i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        db_query = """SELECT 
                          service_id, queue_name, host, port
                      FROM 
                          msgeovilleconfig.message_queue_config
                      WHERE
                          queue_name = %s AND
                          deleted_at IS NULL
                   """

        try:
            gemslog(LogLevel.INFO, f'Request path parameters: {queue_name}', 'API-get_queue_config_by_name')

            if not check_queue_existence(queue_name, db_file, db_section):
                error = NotFoundError('Queue name does not exist', '', '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_queue_config_by_name')
                return {'message': error.to_dict()}, 404

            conf_data = read_from_database_one_row(db_query, (queue_name, ), db_file, db_section, True)

            config_obj = {
                'service_id': conf_data[0],
                'queue_name': conf_data[1],
                'host': conf_data[2],
                'port': conf_data[3]
            }

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_queue_config_by_name')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_queue_config_by_name')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-get_queue_config_by_name')
            return config_obj, 200
