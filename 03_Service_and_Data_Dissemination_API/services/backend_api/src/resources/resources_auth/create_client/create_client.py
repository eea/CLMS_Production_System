########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create OAuth2 client API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_408.http_error_408 import RequestTimeoutError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from init.init_env_variables import oauth2_create_client
from init.namespace_constructor import auth_namespace as api
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from lib.auth_header import auth_header_parser
from models.models_auth.client_models.client_models import auth_client_request_model, auth_client_response_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_408 import error_408_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from requests.exceptions import HTTPError
from oauth.oauth2 import require_oauth
import requests
import traceback


########################################################################################################################
# Resource definition for the create OAuth2 client API call
########################################################################################################################

@api.expect(auth_client_request_model)
@api.header('Content-Type', 'application/json')
class CreateOAuthClient(Resource):
    """ Class for handling the POST request

    This class defines the API call for the create OAuth2 client script. The class consists of one method which accepts
    a POST request. For the POST request a JSON with several parameters is required and defined in the corresponding
    model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', auth_client_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(408, 'Request Timeout', error_408_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating an OAuth2 client

        <p style="text-align: justify">This method defines the handler for the POST request of the create OAuth2 client
        script. It returns the client ID and client secret wrapped into a Python dictionary of the newly created OAuth2
        client.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">The request call sends a HTTP POST request in the background to the OAuth2 server
        with the full name of the client / user. In OAuth2 database a new client will be created and the credentials for
        authentication will be returned. The generated client ID and secret should be kept and not passed to anyone.
        Client ID and secret are used to generate Bearer tokens for the authentication process. This request does not
        create a new customer in the GEMS customer database.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>client_name (str): Full name of the client</i></p></li>
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
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-create_oauth_client')

            payload = {'client_name': req_args['client_name'],
                       'grant_type': 'password\nrefresh_token',
                       'response_type': 'code',
                       'client_uri': '',
                       'redirect_uri': '',
                       'scope': '',
                       'token_endpoint_auth_method': 'client_secret_basic'}

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            response = requests.request('POST', oauth2_create_client, headers=headers, data=payload, timeout=15)

        except requests.exceptions.ReadTimeout:
            error = RequestTimeoutError('Connection timed out while contacting the Authorization server', '', '')
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_oauth_client')
            return {'message': error.to_dict()}, 408

        except HTTPError:
            error = ServiceUnavailableError('Could not connect to OAuth2 server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_oauth_client')
            return {'message': error.to_dict()}, 404

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_oauth_client')
            return {'message': error.to_dict()}, 500

        else:
            if response.status_code == 200:
                gemslog(LogLevel.INFO, f'Request response: {response.json()}', 'API-create_oauth_client')
                return response.json()

            else:
                error = ServiceUnavailableError('Could not contact the Authorization Server', api.payload, '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_oauth_client')
                return {'message': error.to_dict()}, 503
