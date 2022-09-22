########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get customer by filter API call
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
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.general_helper_methods import parameter_and_value_list_generation
from models.models_crm.customer_models.customer_models import customer_list_response_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
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
# Resource definition for the get customer API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetCustomersByFilter(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get customer by filter script. The class consists of one method which
    accepts a GET request. For the GET request a JSON with several additional parameter is required, defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(query_param_parser)
    @api.response(200, 'Operation successful', customer_list_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving a customer by a filter

        <p style="text-align: justify">This method defines the handler for the GET request of the get customer by filter
        script. It returns the customer data stored in the database wrapped into a dictionary defined by corresponding
        model.</p>

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
        <p style="text-align: justify"></p>

        """

        try:
            req_args = query_param_parser.parse_args()
            gemslog(LogLevel.INFO, f"Request payload: {req_args}", 'API-get_customer_filter')

            param_list, val_list = parameter_and_value_list_generation(req_args)

            if not val_list and not param_list:
                db_query = """SELECT 
                                  title, first_name, last_name, email, address, city, zip_code, country, nationality, 
                                  phone_number, company_name 
                              FROM 
                                  customer.customer
                              WHERE
                                  deleted_at IS NULL
                           """

            else:
                db_query = f"""SELECT 
                                   title, first_name, last_name, email, address, city, zip_code, country, nationality, 
                                   phone_number, company_name 
                               FROM 
                                   customer.customer
                               WHERE 
                                   {'AND '.join(param_list)} AND
                                   deleted_at IS NULL
                            """

            customer_data = read_from_database_all_rows(db_query, val_list, database_config_file,
                                                        database_config_section_api, True)

            if customer_data is None or customer_data is False:
                return {'customers': None}, 200

            customer_res = []

            for customer in customer_data:
                customer_obj = {
                    'title': customer[0],
                    'first_name': customer[1],
                    'last_name': customer[2],
                    'email': customer[3],
                    'address': customer[4],
                    'city': customer[5],
                    'zip_code': customer[6],
                    'country': customer[7],
                    'nationality': customer[8],
                    'phone_number': customer[9],
                    'company_name': customer[10]
                }

                customer_res.append(customer_obj)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', req_args, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_customer_filter')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_customer_filter')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', req_args, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_customer_filter')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Successful response: {customer_res}', 'API-get_customer_filter')
            return {'customers': customer_res}, 200
