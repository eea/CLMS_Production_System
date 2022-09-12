########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ list queues GEMS API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import rabbitmq_host, rabbitmq_management_port, rabbitmq_password, rabbitmq_user
from init.namespace_constructor import rabbitmq_namespace as api
from lib.auth_header import auth_header_parser
from models.models_rabbitmq.list_queues.list_queues_model import rabbitmq_response_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
from pyrabbit.api import Client
from pyrabbit.http import HTTPError, NetworkError
import traceback


########################################################################################################################
# Resource definition for the list queues API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class RabbitMQListQueues(Resource):
    """ Class for handling the GET request

    This class defines the API call for the RabbitMQ list queues script. The class consists of one method which accepts
    a GET request. For the GET request no additional parameters are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################
    
    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation successful', rabbitmq_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving the list of available queues in GEMS

        <p style="text-align: justify">This method defines the handler for the GET request of the RabbitMQ list queues
        script. It returns a list of all available queues with the connection parameters stored in the environment
        variables.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the </p>

        """

        try:
            cl = Client(f'{rabbitmq_host}:{rabbitmq_management_port}', rabbitmq_user, rabbitmq_password)

        except HTTPError:
            error = UnauthorizedError('Login credentials derived from the environment variable are incorrect', '', '')
            log('API-rabbitmq_queues_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'messages': error.to_dict()}, 401

        except NetworkError:
            error = ServiceUnavailableError('Could not connect to the RabbitMQ service', '', '')
            log('API-rabbitmq_queues_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'messages': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-rabbitmq_queues_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-rabbitmq_queues_gems', LogLevel.INFO, 'Successfully retrieved the queue names')
            return {'available_queues': [q['name'] for q in cl.get_queues()]}, 200
