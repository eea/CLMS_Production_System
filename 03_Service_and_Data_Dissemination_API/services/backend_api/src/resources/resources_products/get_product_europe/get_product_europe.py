########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get Products for Europe API call
#
# Date created: 24.02.2022
# Date last modified: 24.02.2022
#
# __author__  = Johannes Schmid (schmid@geoville.com)
# __version__ = 22.02
#
########################################################################################################################

from check_message.check_message import check_message
from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from geoville_ms_orderid_generator.generator import generate_orderid
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import service_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence, get_service_id
from models.general_models.general_models import service_success_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_408 import error_408_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_products.products_models import european_products_request_model, products_success_response_model
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the get-products-europe API call
########################################################################################################################

@api.expect(european_products_request_model)
@api.header('Content-Type', 'application/json')
class ProductEurope(Resource):
    """ Class for handling the POST request

    This class defines the API call for getting the specified product for entire Europe.
    The class consists of one method which accepts a POST request. For the POST request the user ID is required,
    defined in the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'user', 'get_product'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Success', products_success_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(408, 'Request Timeout', error_408_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for requesting the specified product for entire Europe

        <p style="text-align: justify">This method defines the handler of the POST request for getting the
        specified product for entire Europe. It is a synchronous call and thus, it returns the requested data
        immediately. To access the service it is necessary to generate a valid Bearer
        token with sufficient access rights, otherwise the request will return a HTTP status code 401 or 403. In case of
        those errors, please contact the GeoVille service team for any support.</p>

        <br><b>Description:</b>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>product (str): Name of the CLC+ Backbone product</i></p></li>
        <li><p><i>user_id (str): User specific client ID</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">After the request was successful, a download link will be returned which
        provides the ordered file.</p>

        """

        order_id = None

        try:
            req_args = api.payload

            payload_check = check_message(req_args)

            if not payload_check[0]:
                error = BadRequestError(f'Payload failed the GeoVille standards: {payload_check[1]}', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products-europe', order_id)
                return {'message': error.to_dict()}, 404

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products-europe', order_id)
                return {'message': error.to_dict()}, 404

            service_id = get_service_id("get_product_europe", database_config_file, database_config_section_api)
            order_id = generate_orderid(req_args['user_id'], service_id, json.dumps(req_args))
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-products-europe', order_id)

            update_query = """UPDATE customer.service_orders
                                  set status = 'RECEIVED'
                              WHERE
                                  order_id = %s;
                           """
            execute_database(update_query, (order_id,), database_config_file, database_config_section_api, True)

            dll = "https://s3.waw2-1.cloudferro.com/swift/v1/AUTH_b9657821e4364f88862ca20a180dc485/clcplus-public/" \
                  "products/CLMS_CLCplus_RASTER_2018_010m_eu_03035_V1_1.tif"

            db_query = """UPDATE 
                              customer.service_orders 
                          SET 
                              status = 'SUCCESS', 
                              result = %s,
                              success = true,
                              order_started = NOW(),
                              order_received = NOW(), 
                              order_stopped = NOW() 
                          WHERE order_id = %s
                       """
            execute_database(db_query, (dll, order_id), database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products-europe', order_id)
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-products-europe', order_id)
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-products-europe', order_id)
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-products-europe', order_id)
            return {
                    'result': dll
                   }, 200
