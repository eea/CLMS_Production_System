########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Stitching API call
#
# Date created: 02.08.2021
# Date last modified: 02.08.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.08
#
########################################################################################################################

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
from lib.database_helper import check_service_name_existence, check_user_existence, get_service_id
from lib.general_helper_methods import publish_to_queue
from models.general_models.general_models import service_success_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_services.task_1_stitching.task_1_stitching_model import task_1_stitching_request_model
from check_message.check_message import check_message
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the stitching (Task 1) API call
########################################################################################################################

@api.expect(task_1_stitching_request_model)
@api.header('Content-Type', 'application/json')
class Task1Stitching(Resource):
    """ Class for handling the POST request

    This class defines the API call for starting the stitching (Task 1) workflow. The class consists of one
    methods which accepts a POST request. For the POST request a JSON with several parameters is required, defined in
    the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'stitching_task_1', 'gaf', 'task_1'])
    @api.expect(auth_header_parser)
    @api.response(202, 'Order Received', service_success_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for the stitching process in task 1

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>processing_unit_name (str): Name of the input PU</i></p></li>
        <li><p><i>surrounding_pus (str): Name of the surrounding PU's</i></p></li>
        <li><p><i>user_id (str): User specific client ID</i></p></li>
        <li><p><i>service_name (str): Unique name of the service to be called. Name should not be changed</i></p></li>
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
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
                return {'message': error.to_dict()}, 404

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
                return {'message': error.to_dict()}, 404

            if not check_service_name_existence(req_args['service_name'], database_config_file,
                                                database_config_section_api):
                error = NotFoundError('Service name does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
                return {'message': error.to_dict()}, 404

            service_id = get_service_id(req_args['service_name'], database_config_file, database_config_section_api)
            order_id = generate_orderid(req_args['user_id'], service_id, json.dumps(req_args))
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-task1_stitching', order_id)

            publish_to_queue(req_args['service_name'], order_id, req_args)

            update_query = """UPDATE customer.service_orders 
                                  set status = 'RECEIVED' 
                              WHERE
                                  order_id = %s;
                           """
            execute_database(update_query, (order_id,), database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
            return {'message': error.to_dict()}, 503

        except Exception as err:
            error = InternalServerErrorAPI(f'Unexpected error occurred: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-task1_stitching', order_id)
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request successful', 'API-task1_stitching', order_id)
            return {
                       'message': 'Your order has been successfully submitted',
                       'links': {
                           'href': f'/services/order_status/{order_id}',
                           'rel': 'services',
                           'type': 'GET'
                       }
                   }, 202
