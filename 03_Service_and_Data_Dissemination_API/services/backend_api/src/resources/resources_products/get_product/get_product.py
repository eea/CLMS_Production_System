########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get Products API call
#
# Date created: 23.07.2021
# Date last modified: 23.07.2021
#
# __author__  = Johannes Schmid (schmid@geoville.com)
# __version__ = 21.07
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
from lib.general_helper_methods import publish_to_queue
from models.general_models.general_models import service_success_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_products.products_models import products_request_model
from oauth.oauth2 import require_oauth
import json
import traceback
import pyproj
import shapely.wkt
from shapely.ops import transform

########################################################################################################################
# Resource definition for the get-products API call
########################################################################################################################

@api.expect(products_request_model)
@api.header('Content-Type', 'application/json')
class Products(Resource):
    """ Class for handling the POST request

    This class defines the API call for starting the get-products workflow. The class consists of one methods which
    accepts a POST request. For the POST request a JSON with several parameters is required, defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'user', 'get_product'])
    @api.expect(auth_header_parser)
    @api.response(202, 'Order Received', service_success_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for requesting the get-products workflow

        <p style="text-align: justify">This method defines the handler of the POST request for starting off the
        get-products processing chain within the GEMS service architecture. It is an asynchronous call and thus, it does
        not return the requested data immediately but generates an order ID. After the request has been submitted
        successfully, a message to a RabbitMQ queue will be send. A listener in the backend triggers the further
        procedure, starting with the job scheduling of the order. The final result will be stored in a database in form
        of a link and can be retrieved via the browser. To access the service it is necessary to generate a valid Bearer
        token with sufficient access rights, otherwise the request will return a HTTP status code 401 or 403. In case of
        those errors, please contact the GeoVille service team for any support.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">By providing an Area of Interest (AOI) a specified product can be ordered.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>product (str): Name of the CLC+ Backbone product</i></p></li>
        <li><p><i>aoi (str): Area of Interest as MultiPolygon (WKT) in WGS84 (EPSG:4326)</i></p></li>
        <li><p><i>user_id (str): User specific client ID</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">After the request was successfully received by the GEMS API, an order ID will be
        created for the submitted job in the GEMS backend and stored in a database with all necessary information for
        the consumer and the system itself. The initial status of the order in the database will be set to 'received'.
        After that the order ID will be returned in form of a Hypermedia link which enables the possibilities to
        programmatically check the status the order by a piece of code of a GEMS API consumer. In the following the
        status of the order can be queried by using the GEMS service route listed below:</p>

        <ul><li><p><i>/services/order_status/{order_id}</i></p></li></ul>

        <p style="text-align: justify">The status of the order will be updated whenever the processing chain reaches the
        next step in its internal calculation. In case of success, the user will receive a link, which provides the
        ordered file. Additionally an e-mail notification is enabled, which sends out an e-mail in case of success, with
        the resulting link or in case of failure, with a possible error explanation.
        </p>

        """

        order_id = None

        try:
            req_args = api.payload

            payload_check = check_message(req_args)

            if not payload_check[0]:
                error = BadRequestError(f'Payload failed the GeoVille standards: {payload_check[1]}', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products', order_id)
                return {'message': error.to_dict()}, 404

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products', order_id)
                return {'message': error.to_dict()}, 404

            # get area of aoi
            reproject = pyproj.Transformer.from_crs(pyproj.CRS('EPSG:4326'), pyproj.CRS('EPSG:3857'), always_xy=True).transform
            aoi_metric = transform(reproject, shapely.wkt.loads(req_args['aoi']))
            aoi_area = aoi_metric.area * 1.0E-6
            if aoi_area > 5000000:
                error = "The requested AOI is too big (> 5 Mio. km²). Please note that countries and entire Europe " \
                        "can be requested with other endpoints."
                gemslog(LogLevel.WARNING, f"'message': {error}", 'API-products', order_id)
                return {'message': error}, 404


            service_id = get_service_id("get_product", database_config_file, database_config_section_api)
            order_id = generate_orderid(req_args['user_id'], service_id, json.dumps(req_args))
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-products', order_id)

            publish_to_queue("get_product", order_id, req_args)

            update_query = """UPDATE customer.service_orders 
                                  set status = 'RECEIVED' 
                              WHERE
                                  order_id = %s;
                           """
            execute_database(update_query, (order_id,), database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-products', order_id)
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-products', order_id)
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-products', order_id)
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-products', order_id)
            return {
                       'message': 'Your order has been successfully submitted',
                       'links': {
                           'href': f'/services/order_status/{order_id}',
                           'area': '%.2f km2' % aoi_area,
                           'rel': 'services',
                           'type': 'GET'
                       }
                   }, 202
