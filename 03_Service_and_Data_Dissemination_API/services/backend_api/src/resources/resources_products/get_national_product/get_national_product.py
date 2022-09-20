########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get National Products API call
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
from lib.general_helper_methods import publish_to_queue
from lib.database_helper import check_user_existence, get_service_id
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_408 import error_408_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_products.products_models import national_products_request_model, products_success_response_model
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the get-national-products API call
########################################################################################################################

@api.expect(national_products_request_model)
@api.header('Content-Type', 'application/json')
class NationalProducts(Resource):
    """ Class for handling the POST request

    This class defines the API call for getting the specified product for a nation of choice.
    The class consists of one method which accepts a GET request. For the GET request the user ID is required,
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
        """ POST definition for requesting the specified product for a nation of choice.

        <p style="text-align: justify">This method defines the handler of the POST request for getting the
        specified product for a nation of choice. It is a synchronous call and thus, it returns the requested data
        immediately. To access the service it is necessary to generate a valid Bearer
        token with sufficient access rights, otherwise the request will return a HTTP status code 401 or 403. In case of
        those errors, please contact the GeoVille service team for any support.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">By providing a country name a specified product can be retrieved.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>product (str): Name of the CLC+ Backbone product</i></p></li>
        <li><p><i>nation (str): Country name in English (e.g. Germany)</i></p></li>
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
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-national-products', order_id)
                return {'message': error.to_dict()}, 404

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-national-products', order_id)
                return {'message': error.to_dict()}, 404

            service_id = get_service_id("get_national_product", database_config_file, database_config_section_api)
            order_id = generate_orderid(req_args['user_id'], service_id, json.dumps(req_args))
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-national-products', order_id)

            # ToDo: uncomment if asynchronous job wanted (not ready yet)
            # publish_to_queue("get_national_product", order_id, req_args)

            update_query = """UPDATE customer.service_orders
                                  set status = 'RECEIVED'
                              WHERE
                                  order_id = %s;
                           """
            execute_database(update_query, (order_id,), database_config_file, database_config_section_api, True)

            national_info = {
                "ALBANIA": {"country_code": "AL", "epsg": "02462"},
                "AUSTRIA": {"country_code": "AT", "epsg": "31287"},
                "BOSNIA AND HERZEGOVINA": {"country_code": "BA", "epsg": "03908"},
                "BELGIUM": {"country_code": "BE", "epsg": "03812"},
                "BULGARIA": {"country_code": "BG", "epsg": "32635"},
                "SWITZERLAND": {"country_code": "CH", "epsg": "02056"},
                "CYPRUS": {"country_code": "CY", "epsg": "32636"},
                "CZECH REPUBLIC": {"country_code": "CZ", "epsg": "05514"},
                "GERMANY": {"country_code": "DE", "epsg": "32632"},
                "DENMARK": {"country_code": "DK", "epsg": "25832"},
                "ESTONIA": {"country_code": "EE", "epsg": "03301"},
                "SPAIN": {"country_code": "ES", "epsg": "25830"},
                "SPAIN (CANARIES)": {"country_code": "ES", "epsg": "32628"},
                "FINLAND": {"country_code": "FI", "epsg": "03067"},
                "FRANCE": {"country_code": "FR", "epsg": "02154"},
                "GREAT BRITAIN": {"country_code": "GB", "epsg": "27700"},
                "GUERNSEY (CHANNEL ISLANDS)": {"country_code": "GB", "epsg": "03108"},
                "GREECE": {"country_code": "GR", "epsg": "02100"},
                "CROATIA": {"country_code": "HR", "epsg": "03765"},
                "HUNGARY": {"country_code": "HU", "epsg": "23700"},
                "IRELAND": {"country_code": "IE", "epsg": "02157"},
                "ICELAND": {"country_code": "IS", "epsg": "05325"},
                "ITALY": {"country_code": "IT", "epsg": "32632"},
                "JERSEY (CHANNEL ISLANDS)": {"country_code": "GB", "epsg": "03109"},
                "LIECHTENSTEIN": {"country_code": "LI", "epsg": "02056"},
                "LITHUANIA": {"country_code": "LT", "epsg": "03346"},
                "LUXEMBOURG": {"country_code": "LU", "epsg": "02169"},
                "LATVIA": {"country_code": "LV", "epsg": "03059"},
                "MONTENEGRO": {"country_code": "ME", "epsg": "25834"},
                "FYR OF MACEDONIA": {"country_code": "MK", "epsg": "06204"},
                "MALTA": {"country_code": "MT", "epsg": "23033"},
                "NORTHERN IRELAND": {"country_code": "NI", "epsg": "29903"},
                "NETHERLANDS": {"country_code": "NL", "epsg": "28992"},
                "NORWAY": {"country_code": "NO", "epsg": "25833"},
                "POLAND": {"country_code": "PL", "epsg": "02180"},
                "PORTUGAL": {"country_code": "PT", "epsg": "03763"},
                "PORTUGAL (AZORES CENTRAL AND EASTERN GROUP)": {"country_code": "PT", "epsg": "05015"},
                "PORTUGAL (AZORES WESTERN GROUP)": {"country_code": "PT", "epsg": "05014"},
                "PORTUGAL (MADEIRA)": {"country_code": "PT", "epsg": "05016"},
                "ROMANIA": {"country_code": "RO", "epsg": "03844"},
                "SERBIA": {"country_code": "RS", "epsg": "25834"},
                "SWEDEN": {"country_code": "SE", "epsg": "03006"},
                "SLOVENIA": {"country_code": "SI", "epsg": "03912"},
                "SLOVAKIA": {"country_code": "SK", "epsg": "05514"},
                "TURKEY": {"country_code": "TR", "epsg": "00000"},
                "KOSOVO UNDER UNSCR 1244/99": {"country_code": "KS", "epsg": "03909"},
            }
            
            country, epsg = national_info[req_args['nation'].upper()].values()
            if req_args['product'] == "Raster":
                file_name = f"CLMS_CLCplus_RASTER_2018_010m_{country.lower()}_{epsg}_V1_1.zip"
            else:
                file_name = f"CLMS_CLCplus_VECTOR_2018_{country.upper()}_{epsg}_V1_0.zip"
            dll = f"https://s3.waw2-1.cloudferro.com/swift/v1/AUTH_b9657821e4364f88862ca20a180dc485/clcplus-public/" \
                  f"products/national/{file_name}"
            
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
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-national-products', order_id)
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-national-products', order_id)
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-national-products', order_id)
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-national-products', order_id)
            return {
                    'result': dll
                   }, 200
            #return {
            #           'message': 'Your order has been successfully submitted',
            #           'links': {
            #               'href': f'/services/order_status/{order_id}',
            #               'rel': 'services',
            #               'type': 'GET'
            #           }
            #       }, 202
