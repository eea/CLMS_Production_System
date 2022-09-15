########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create customer API call
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
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.request_helper import create_oauth_client
from models.models_crm.customer_models.customer_models import customer_model, customer_creation_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_408 import error_408_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the create customer API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class CreateCustomer(Resource):
    """ Class for handling the POST request

    This class defines the API call for the create customer script. The class consists of one method which accepts a
    POST request. For the POST request a JSON with several parameters is required and defined in the corresponding
    model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(body=customer_model, parser=auth_header_parser)
    @api.response(201, 'Operation successful', customer_creation_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(408, 'Request Timeout', error_408_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating a new customer

        <p style="text-align: justify">This method defines the handler for the POST request of the create customer
        script. It returns a message wrapped into a dictionary containing the .</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This service creates a GEMS user in the GEMS customer database and in the OAuth2
        database. First a POST request to the OAuth2 server will be send with the full name of the client to be created.
        A new OAuth2 user is created and the OAuth2 client ID and client secret is returned. The client ID will be
        further used as primary key for the customer table. The new customer with all submitted request parameters will
        be created and the client ID and client secret returned.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>title (str): </i></p></li>
        <li><p><i>first_name (str): </i></p></li>
        <li><p><i>last_name (str): </i></p></li>
        <li><p><i>email (str): </i></p></li>
        <li><p><i>password (str): </i></p></li>
        <li><p><i>address (str): </i></p></li>
        <li><p><i>city (str): </i></p></li>
        <li><p><i>zip_code (str): </i></p></li>
        <li><p><i>country (str): </i></p></li>
        <li><p><i>nationality (str): optional</i></p></li>
        <li><p><i>phone_number (str): optional</i></p></li>
        <li><p><i>company_name (str): </i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON that contains 2 key value pairs. The
        client ID is a unique identifier of a client in the OAuth2 database and in the GEMS database for GEMS user. The
        client secret could be seen as a password for the GEMS user, used only for the Bearer token generation.</p>
        <ul>
        <li><p><i>client_id (str): Unique client ID of a GEMS customer for authentication</i></p></li>
        <li><p><i>client_secret (str): Unique client secret of a GEMS customer for authentication</i></p></li>
        </ul>

        """

        try:
            req_args = api.payload
            log('API-create_customer', LogLevel.INFO, f'Request payload: {req_args}')

            request_response = create_oauth_client(f"{req_args['first_name']} {req_args['last_name']}")

            if request_response[0] is None:
                return request_response[1], request_response[2]

            nationality = None if 'phone' not in req_args else req_args['nationality']
            phone = None if 'phone' not in req_args else req_args['phone']

            db_query = """INSERT INTO customer.customer
                          ( 
                              customer_id, title, first_name, last_name, email, address, city, zip_code, country, 
                              nationality, phone_number, company_name
                          ) 
                          VALUES
                          (
                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                          );
                       """

            execute_database(db_query,
                             (request_response[0]['client_id'], req_args['title'], req_args['first_name'],
                              req_args['last_name'], req_args['email'], req_args['address'], req_args['city'],
                              req_args['zip_code'], req_args['country'], nationality, phone, req_args['company_name']),
                             database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-create_customer', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-create_customer', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-create_customer', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-create_customer', LogLevel.INFO, f"Successfully created new customer {req_args['last_name']}")
            return {
                       'client_id': request_response[0]['client_id'],
                       'client_secret': request_response[0]['client_secret']
                   }, 201
