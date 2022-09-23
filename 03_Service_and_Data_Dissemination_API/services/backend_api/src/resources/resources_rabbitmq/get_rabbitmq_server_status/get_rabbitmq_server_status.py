########################################################################################################################
#
# RabbitMQ server status GEMS API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import rabbitmq_host, rabbitmq_management_port, rabbitmq_password, rabbitmq_user
from init.namespace_constructor import rabbitmq_namespace as api
from lib.auth_header import auth_header_parser
from models.models_rabbitmq.server_status.server_status_model import rabbitmq_response_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
from pyrabbit.api import Client
from pyrabbit.http import HTTPError, NetworkError
import traceback


########################################################################################################################
# Resource definition for the server status API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class RabbitMQServerStatus(Resource):
    """ Class for handling the GET requests

    This class defines the API call for the RabbitMQ server status script. The class consists of one method which
    accepts a GET request. For the GET request no additional parameters are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Success', rabbitmq_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    @api.marshal_with(rabbitmq_response_model)
    def get(self):
        """ GET definition for retrieving the server status of GEMS

        <p style="text-align: justify">This method defines the handler for the GET request of the RabbitMQ server status
        script. It returns about the server status of GEMS RabbitMQ instance with the connection parameters stored in
        the environment variables.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the </p>

        """

        stat_obj = {'host': rabbitmq_host}

        try:
            cl = Client(f'{rabbitmq_host}:{rabbitmq_management_port}', rabbitmq_user, rabbitmq_password)
            server_stat = cl.is_alive()

            if server_stat:
                stat_obj['server_status'] = 'RabbitMQ service is up and running'

            else:
                stat_obj['server_status'] = 'The Virtual machine is up but the RabbitMQ service is not available'

        except HTTPError:
            error = UnauthorizedError('Login credentials derived from the environment variable are incorrect', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_server_status')
            return {'message': error.to_dict()}, 401

        except NetworkError:
            error = ServiceUnavailableError('Could not connect to the RabbitMQ service', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_server_status')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_server_status')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, 'Successfully retrieved the server status', 'API-rabbitmq_server_status')
            return stat_obj, 200
