########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Adds a new API queue configuration to the database
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import config_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_service_existence, check_queue_existence
from models.models_config.queue_config.queue_config_models import add_queue_config_model, queue_creation_success_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the inserting a new queue configuration API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class AddQueueConfig(Resource):
    """ Class for handling the POST request

    This class defines the API call for the add queue configuration script. The class consists of one method which
    accepts a POST request. For the POST request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(body=add_queue_config_model, parser=auth_header_parser)
    @api.response(201, 'Operation successful', queue_creation_success_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for adding a new queue configuration

        <p style="text-align: justify">This method defines the handler for the POST request of the add queue
        configuration script. It returns a message wrapped into a dictionary about the status of the insertion
        operation.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>service_id (str): Full name of the client</i></p></li>
        <li><p><i>queue_name (str): Full name of the client</i></p></li>
        <li><p><i>host (str): Full name of the client</i></p></li>
        <li><p><i>port (str): Full name of the client</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        try:
            req_args = api.payload
            log('API-add_queue_config', LogLevel.INFO, f'Request: {req_args}')

            if check_queue_existence(req_args['queue_name'], database_config_file, database_config_section_api):
                error = NotFoundError('Queue name exists already', '', '')
                log('API-add_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            if not check_service_existence(req_args['service_id'], database_config_file, database_config_section_api):
                error = NotFoundError('Service ID does not exist', '', '')
                log('API-add_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            db_query = """INSERT INTO msgeovilleconfig.message_queue_config
                          ( 
                              queue_name, host, port, service_id
                          ) 
                          VALUES
                          (
                              %s, %s, %s, %s
                          )
                       """

            execute_database(db_query, (req_args['queue_name'], req_args['host'], req_args['port'],
                                        req_args['service_id']), database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-add_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-add_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-add_queue_config', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            return {'service_id': req_args['service_id'],
                    'queue_name': req_args['queue_name']}, 201
