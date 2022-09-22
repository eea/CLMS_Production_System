########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get customer by ID API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence
from models.models_crm.customer_models.customer_models import customer_filter_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the get customer by ID API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('user_id', 'User ID to be requested')
class GetCustomerById(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get customer by ID script. The class consists of one method which accepts a
    GET request. For the GET request one path variable is required and defined in the corresponding class method.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation was successful', customer_filter_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, user_id):
        """ GET definition for retrieving a customer by a ID

        <p style="text-align: justify">This method defines the handler for the GET request of the get customer by ID
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
            gemslog(LogLevel.INFO, f'Request path parameter {user_id}', 'API-get_customers_by_id')

            if not check_user_existence(user_id, database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_customers_by_id')
                return {'message': error.to_dict()}, 404

            db_query = """SELECT 
                              title, first_name, last_name, email, address, city, zip_code, country, nationality, 
                              phone_number, company_name 
                          FROM 
                              customer.customer
                          WHERE 
                              customer_id = %s AND
                              deleted_at IS NULL
                       """

            customer = read_from_database_one_row(db_query, (user_id,), database_config_file,
                                                  database_config_section_api, True)
            customer_data = {
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

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_customers_by_id')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_customers_by_id')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_customers_by_id')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Successful response: {customer_data}', 'API-get_customers_by_id')
            return customer_data, 200
