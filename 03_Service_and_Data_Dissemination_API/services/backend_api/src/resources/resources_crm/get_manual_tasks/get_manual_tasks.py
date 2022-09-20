########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get all services API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from error_classes.http_error_422.http_error_422 import UnprocessableEntityError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.general_helper_methods import parameter_and_value_list_generation
from lib.auth_header import auth_header_parser
from lib.database_helper import check_service_name_existence, check_processing_unit_exists, check_subproduction_unit_exists
from models.models_crm.manual_tasks_models.manual_tasks_models import task_query_list_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_422 import error_422_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Query parameter definition of the GET request
########################################################################################################################

query_param_parser = auth_header_parser.copy()
query_param_parser.add_argument('subproduction_unit', location='args', type=str, required=False,
                                help='Sub-Production Unit', trim=True)
query_param_parser.add_argument('processing_unit', location='args', type=str, required=False,
                                help='Processing Unit', trim=True)
query_param_parser.add_argument('service_name', location='args', type=str, required=False,
                                help='Name of the automatic service', trim=True)
query_param_parser.add_argument('order_status', location='args', type=str, required=False, choices=('not_started', 'in_progress', 'failed', 'finished'),
                                help='Status of the service order', trim=True)
query_param_parser.add_argument('task_name', location='args', type=str, required=False,
                                help='Name of the manual task', trim=True)
query_param_parser.add_argument('task_status', location='args', type=str, required=False, choices=('in_progress', 'failed', 'finished'),
                                help='Status of the manual task', trim=True)
########################################################################################################################
# Resources definition for the get service orders API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetManualTasks(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get service orders script. The class consists of one method which accepts a
    GET request. For the GET request no additional parameter are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(query_param_parser)
    @api.response(200, 'Operation was successful', task_query_list_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving all services

        <p style="text-align: justify">This method defines the handler for the GET request of the get service orders
        script. It returns all service data stored in the database wrapped into a dictionary defined by corresponding
        model.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        try:
            req_args = query_param_parser.parse_args()
            gemslog(LogLevel.INFO, 'Request path parameter: {}'.format(req_args),
                    'API-get_manual_tasks')

            if req_args['order_status'] == 'not_started':
                req_args.update({'order_status': 'RECEIVED OR order_status = QUEUED'})
            elif req_args['order_status'] == 'in_progress':
                req_args.update({'order_status': 'RUNNING'})
            elif req_args['order_status'] == 'failed':
                req_args.update({'order_status': 'FAILED'})
            elif req_args['order_status'] == 'finished':
                req_args.update({'order_status': 'SUCCESS'})

            if req_args['task_status'] == 'in_progress':
                req_args.update({'task_status': 'RUNNING'})
            elif req_args['task_status'] == 'failed':
                req_args.update({'task_status': 'FAILED'})
            elif req_args['task_status'] == 'finished':
                req_args.update({'task_status': 'SUCCESS'})

            if req_args['service_name'] and not check_service_name_existence(req_args['service_name'], database_config_file, database_config_section_api):
                error = BadRequestError('Service name does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_manual_tasks')
                return {'message': error.to_dict()}, 400

            # check if subproduction unit exists
            subproduction_unit_exists = check_subproduction_unit_exists(req_args['subproduction_unit'], database_config_file,
                                                                  database_config_section_api)
            if req_args['subproduction_unit'] and not subproduction_unit_exists:
                error = UnprocessableEntityError('Sub-Production unit ({0}) does not exist in database'.format(
                    req_args['subproduction_unit']), '', '')
                return {'message': error.to_dict()}, 422

            # Check if processing unit exists
            processing_unit_exists = check_processing_unit_exists(req_args['processing_unit'], database_config_file,
                                                                  database_config_section_api)
            if req_args['processing_unit'] and not processing_unit_exists:
                error = UnprocessableEntityError('Processing unit ({0}) does not exist in database'.format(
                    req_args['processing_unit']), '', '')
                return {'message': error.to_dict()}, 422

            param_list, val_list = parameter_and_value_list_generation(req_args)

            if not val_list and not param_list:
                db_query = """SELECT DISTINCT
                          ts.subproduction_unit,
                          ts.processing_unit, 
                          ts.service_name,
                          ts.order_status,
                          ts.order_id,
                          ts.task_name,
                          ts.task_status,
                          ts.task_result
                      FROM 
                          customer.tasks_and_services ts
                           """

            else:
                db_query = f"""SELECT DISTINCT
                          ts.subproduction_unit,
                          ts.processing_unit, 
                          ts.service_name,
                          ts.order_status,
                          ts.order_id,
                          ts.task_name,
                          ts.task_status,
                          ts.task_result
                      FROM 
                          customer.tasks_and_services ts
                               WHERE 
                                   {'AND '.join(param_list)}
                            """

            service_data = read_from_database_all_rows(db_query, val_list,
                                                       database_config_file, database_config_section_api,
                                                       True)
            res_array = []

            for service in service_data:
                service_obj = {
                    'subproduction_unit': service[0],
                    'processing_unit': service[1],
                    'service_name': service[2],
                    'order_status': service[3],
                    'order_id': service[4],
                    'task_name': service[5],
                    'task_status': service[6],
                    'task_result': service[7]
                }

                res_array.append(service_obj)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_services')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_services')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Successfully queried all services', 'API-get_services')
            return {'tasks': res_array}, 200
