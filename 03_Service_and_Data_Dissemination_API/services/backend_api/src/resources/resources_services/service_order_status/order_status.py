########################################################################################################################
#
# Status order API call
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
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import service_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import query_order_status
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_services.service_order_status.order_status_model import order_status_response_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the status order API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class OrderStatus(Resource):
    """ Class for handling the GET request

    This class defines the API call for receiving the status of a client's order. The class consists of one methods
    which accepts a GET request. For the POST request a JSON with one parameters is required, defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', order_status_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, order_id):
        """ GET definition for retrieving the order status

        <p style="text-align: justify">This method defines the handler for the GET request for receiving the status of a
        GEMS customers order. The service receives the current status from the database for the specified order ID and
        returns the link to a possible result file.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">The GEMS service route 'order status' was designed to query the status of an
        asynchronous GEMS service what enables the possibility to programmatically check the result of a submitted
        order and further process the expected result file. An order can have the following states:</p>
        <ul>
        <li><p><i>FAILED – An unexpected error occurred during the execution of the service</i></p></li>
        <li><p><i>SUCCESS – Service calculation was successful</i></p></li>
        <li><p><i>QUEUED – Submitted request is in the waiting list</i></p></li>
        <li><p><i>RECEIVED – API received the service request and created an order ID</i></p></li>
        <li><p><i>RUNNING – Service is being calculated at the moment</i></p></li>
        <li><p><i>INVALID – It indicates that there are no available satellite image for the date and tile, the consumer
        requested</i></p></li>
        </ul>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Path parameter:</b>
        <ul>
        <li><p><i>order_id: Order ID received from a triggered asynchronous GEMS service</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON which contains an object with three key
        value pairs.</p>
        <ul>
        <li><p><i>order_id: Order ID received from the triggered asynchronous GEMS service</i></p></li>
        <li><p><i>status: Status of the submitted service</i></p></li>
        <li><p><i>result: link to the final result file or NULL if the process is still running or aborted</i></p></li>
        </ul>

        """

        try:
            order_res = query_order_status(order_id, database_config_file, database_config_section_api)

            if order_res is None or order_res is False:
                error = NotFoundError(f'No database entry found for order ID: {order_id}', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-order_status')
                return {'message': error.to_dict()}, 404

            if order_res[2]:
                return {
                    'order_id': order_id,
                    'status': order_res[0],
                    'result': order_res[1]
                }

            else:
                return {
                    'order_id': order_id,
                    'status': order_res[0],
                    'result': None
                }

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-order_status')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', '', traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-order_status')
            return {'message': error.to_dict()}, 500
