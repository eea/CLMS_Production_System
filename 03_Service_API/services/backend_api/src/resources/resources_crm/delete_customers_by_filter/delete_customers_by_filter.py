########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Delete customer by filter API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database, read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api, database_config_section_oauth
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.general_helper_methods import parameter_and_value_list_generation
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback

########################################################################################################################
# Query parameter definition of the GET request
########################################################################################################################

query_param_parser = auth_header_parser.copy()
query_param_parser.add_argument('title', location='args', type=str, help='Title', trim=True)
query_param_parser.add_argument('first_name', location='args', type=str, help='First name')
query_param_parser.add_argument('last_name', location='args', type=str, help='Last name')
query_param_parser.add_argument('email', location='args', type=str, help='E-mail address')
query_param_parser.add_argument('address', location='args', type=str, help='Address 1')
query_param_parser.add_argument('zip_code', location='args', type=str, help='Zip Code')
query_param_parser.add_argument('city', location='args', type=str, help='City')
query_param_parser.add_argument('country', location='args', type=str, help='Country')
query_param_parser.add_argument('nationality', location='args', type=str, help='Nationality')
query_param_parser.add_argument('phone', location='args', type=str, help='Phone number')
query_param_parser.add_argument('company_name', location='args', type=str, help='Company name')


########################################################################################################################
# Resource definition for the delete customer by filter API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class DeleteCustomersByFilter(Resource):
    """ Class for handling the DELETE request

    This class defines the API call for the delete customer by filter script. The class consists of one method which
    accepts a DELETE request. For the DELETE request a JSON with several additional parameter is required, defined
    in the corresponding request model.

    """

    ####################################################################################################################
    # Method for handling the DELETE request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=query_param_parser)
    @api.response(204, 'Operation successful')
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def delete(self):
        """ DELETE definition for removing customers by filter

        <p style="text-align: justify">This method defines the handler for the DELETE request of the delete all
        customers by filter script. It returns no message body and thus no contents. In contrast it returns the HTTP
        status code 204. If no filter option is specified all customers will be deleted.</p>

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
            req_args = query_param_parser.parse_args()
            log('API-delete_customer_filter', LogLevel.INFO, f'Request payload: {req_args}')

            param_list, val_list = parameter_and_value_list_generation(req_args)

            if not val_list and not param_list:
                db_query_api = "DELETE FROM customer.customer"
                db_query_oauth = "DELETE FROM public.oauth2_client"
                db_query_token = "DELETE FROM public.oauth2_token"

                execute_database(db_query_api, val_list, database_config_file, database_config_section_api, True)
                execute_database(db_query_oauth, val_list, database_config_file, database_config_section_oauth, True)
                execute_database(db_query_token, val_list, database_config_file, database_config_section_oauth, True)

            else:
                db_query_api = f"DELETE FROM customer.customer WHERE {'and '.join(param_list)} RETURNING user_id"
                db_query_oauth = f"DELETE FROM public.oauth2_client WHERE client_id = %s"
                db_query_token = f"DELETE FROM public.oauth2_token WHERE client_id = %s"

                returned_client_ids = read_from_database_all_rows(db_query_api, val_list, database_config_file,
                                                                  database_config_section_api, True)

                if returned_client_ids is not None or returned_client_ids is not False:
                    for client_tuple in returned_client_ids:
                        execute_database(db_query_oauth, (client_tuple[0], ), database_config_file,
                                         database_config_section_oauth, True)
                        execute_database(db_query_token, (client_tuple[0],), database_config_file,
                                         database_config_section_oauth, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-delete_customer_filter', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-delete_customer_filter', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-delete_customer_filter', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-delete_customer_filter', LogLevel.INFO, 'The filtered list of customer data has been deleted')
            return '', 204
