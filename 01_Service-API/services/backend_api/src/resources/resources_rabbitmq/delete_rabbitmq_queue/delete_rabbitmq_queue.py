########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ purge queue GEMS API call
#
# Date created: 20.08.2019
# Date last modified: 11.02.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.02
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import (rabbitmq_host, rabbitmq_management_port, rabbitmq_password, rabbitmq_user,
                                     rabbitmq_virtual_host)
from init.namespace_constructor import rabbitmq_namespace as api
from lib.auth_header import auth_header_parser
from lib.rabbitmq_helper import list_queue_names, purge_queue
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
from pyrabbit.api import Client
from pyrabbit.http import HTTPError, NetworkError
import traceback


########################################################################################################################
# Resource definition for the purge queue API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('queue_name', 'Queue name to be deleted')
class DeleteRabbitMQQueue(Resource):
    """ Class for handling the DELETE request

    This class defines the API call for the RabbitMQ purge queue script. The class consists of one method which accepts
    a DELETE request. For the DELETE request a JSON with 2 parameters is required, defined in the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the DELETE request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(204, 'Operation successful')
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def delete(self, queue_name):
        """ DELETE definition for removing a queue on the GEMS RabbitMQ instance

        <p style="text-align: justify">This method defines the handler for the DELETE request of the RabbitMQ purge
        queue script. It returns no message body and thus no contents. In contrast it returns the HTTP status code 204.
        </p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Path parameter:</b>
        <ul>
        <li><p><i>client_id (str): </i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the DELETE request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicates an error during the execution.</p>

        """

        try:
            cl = Client(f'{rabbitmq_host}:{rabbitmq_management_port}', rabbitmq_user, rabbitmq_password)

            if queue_name not in list_queue_names(cl):
                error = NotFoundError(f"Specified queue name does not exist: {queue_name}", '', '')
                log('API-delete_rabbitmq_queue_gems', LogLevel.WARNING, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            purge_result = purge_queue(cl, rabbitmq_virtual_host, queue_name)

            if purge_result[0] is False:
                error = InternalServerErrorAPI(f'Unexpected Error: {purge_result[1]}', '', '')
                log('API-delete_rabbitmq_queue_gems', LogLevel.ERROR, 'Successfully deleted queue')
                return {'message': error.to_dict()}, 500

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', '', '')
            log('API-delete_rabbitmq_queue_gems', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except HTTPError:
            error = UnauthorizedError('Submitted login credentials are incorrect', '', '')
            log('API-delete_rabbitmq_queue_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 401

        except NetworkError:
            error = ServiceUnavailableError('Could not connect to the specified RabbitMQ service', '', '')
            log('API-delete_rabbitmq_queue_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', '', traceback.format_exc())
            log('API-delete_rabbitmq_queue_gems', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-delete_rabbitmq_queue_gems', LogLevel.ERROR, 'Successfully deleted queue')
            return '', 204
