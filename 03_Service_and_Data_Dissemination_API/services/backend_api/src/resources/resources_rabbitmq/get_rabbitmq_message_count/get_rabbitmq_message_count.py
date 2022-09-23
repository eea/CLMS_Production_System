########################################################################################################################
#
# RabbitMQ message count API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import (rabbitmq_host, rabbitmq_management_port, rabbitmq_password, rabbitmq_user,
                                     rabbitmq_virtual_host)
from init.namespace_constructor import rabbitmq_namespace as api
from lib.auth_header import auth_header_parser
from lib.rabbitmq_helper import get_queue_message_count, list_queue_names
from models.models_rabbitmq.message_count.message_count_model import message_count_model
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
# Resource definition for the list queues API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('queue_name', 'Queue name to count the messages of')
class RabbitMQMessageCount(Resource):
    """ Class for handling the GET request

    This class defines the API call for the RabbitMQ message count script. The class consists of one method which accepts
    a GET request. For the GET request no additional parameters are required.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', message_count_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, queue_name):
        """ GET definition for retrieving the message count of a queue in GEMS

        <p style="text-align: justify">This method defines the handler for the GET request of the RabbitMQ message
        count script. It returns a dictionary with message count of the queue stored in the path variable with the
        connection parameters of a RabbitMQ service stored in the environment variables.</p>

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

            new_queue_name = None
            for filter_item in filter(lambda x: queue_name in x, list_queue_names(cl)):
                new_queue_name = filter_item

            if new_queue_name is None:
                error = NotFoundError(f'Specified queue name does not exist: {queue_name}', '', '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_message_count_gems')
                return {'message': error.to_dict()}, 404

            message_count = get_queue_message_count(cl, rabbitmq_virtual_host, new_queue_name)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-rabbitmq_message_count')
            return {'message': error.to_dict()}, 400

        except HTTPError:
            error = UnauthorizedError('Submitted login credentials are incorrect', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_message_count')
            return {'message': error.to_dict()}, 401

        except NetworkError:
            error = ServiceUnavailableError('Could not connect to the RabbitMQ service', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_message_count')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-rabbitmq_message_count')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, 'Successful requested the RabbitMQ message count', 'API-rabbitmq_message_count')
            return {"virtual_host": rabbitmq_virtual_host,
                    "queue_name": queue_name,
                    "message_count": message_count}, 200
