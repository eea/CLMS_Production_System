########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get Bearer token API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_408.http_error_408 import RequestTimeoutError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from flask_restx import Resource
from init.init_env_variables import (database_config_file, database_config_section_oauth, oauth2_generate_token,
                                     oauth2_password, oauth2_user)
from init.namespace_constructor import auth_namespace as api
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from lib.database_helper import (check_client_id_existence, check_client_id_secret_existence,
                                 check_client_secret_existence, get_scope_by_id)
from models.models_auth.access_token_models.access_token_models import bearer_token_request_model, bearer_token_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_408 import error_408_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from requests.exceptions import HTTPError
import requests
import traceback


########################################################################################################################
# Resource definition for the get Bearer token API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetBearerToken(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get Bearer token script. The class consists of one method which accepts a
    GET request. For the GET request two path parameters are required.
    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @api.expect(bearer_token_request_model)
    @api.response(200, 'Operation successful', bearer_token_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(408, 'Request Timeout', error_408_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for retrieving an OAuth2 Bearer token

        <p style="text-align: justify">This method defines the handler for the GET request of the get Bearer token
        request. It returns all the information from the OAuth2 server</p>

        <br><b>Description:</b>
        <p style="text-align: justify">The GEMS microservice architecture has foreseen an OAuth2 authentication and
        authorisation server for handling the GEMS costumers login and the access to GEMS services. To gain access of
        the services of the GEMS API it is necessary for each consumer to create a new Bearer token from this service
        route. The token type and the token itself are needed for service routes which require an authorisation header.
        In the authorisation header, the API consumer need to write the token in the following format "Bearer XXXX".</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>None</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>client_id (str): User specific client ID provided by the GEMS administration team</i></p></li>
        <li><p><i>client_secret (str): User specific client secret provided by the GEMS administration team</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the submitted request is an automatically created JSON response of
        the OAuth2 server which returns the following parameters:</p>
        <ul>
        <li><p><i>access_token: Token needed for all the authorisation steps</i></p></li>
        <li><p><i>expires_in: Expiration time of the token in seconds</i></p></li>
        <li><p><i>refresh_token: Can be used to obtain a renewed access token</i></p></li>
        <li><p><i>token_type: Type of the token, in case of GEMS, it is always Bearer. Needed in the authorisation header</i></p></li>
        </ul>

        """

        try:
            req_args = api.payload
            log('API-get_bearer_token', LogLevel.INFO, f'Request payload: {req_args}')

            if not check_client_id_existence(req_args['client_id'], database_config_file, database_config_section_oauth):
                error = NotFoundError('Client ID does not exist', '', '')
                log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            if not check_client_secret_existence(req_args['client_secret'], database_config_file, database_config_section_oauth):
                error = NotFoundError('Client secret does not exist', '', '')
                log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            if not check_client_id_secret_existence(req_args['client_id'], req_args['client_secret'],
                                                    database_config_file, database_config_section_oauth):
                error = BadRequestError('Invalid client credentials combination', '', '')
                log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 400

            scope = get_scope_by_id(req_args['client_id'], database_config_file, database_config_section_oauth)

            files = {
                'grant_type': (None, "password"),
                'username': (None, oauth2_user),
                'password': (None, oauth2_password),
                'scope': (None, scope),
            }

            response = requests.post(oauth2_generate_token, files=files, auth=(req_args['client_id'],
                                                                               req_args['client_secret']), timeout=15)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', '', traceback.format_exc())
            log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except requests.exceptions.ReadTimeout:
            error = RequestTimeoutError('Connection timed out while contacting the Authorization server', '', '')
            log('API-get_bearer_token', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 408

        except HTTPError:
            error = NotFoundError(f'Could not connect to OAuth2 server', '', traceback.format_exc())
            log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 404

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            if response.status_code == 200:
                log('API-get_bearer_token', LogLevel.INFO, f'Request response: {response.json()}')
                return response.json()

            elif response.status_code == 401:
                error = UnauthorizedError('Submitted client is invalid', '', '')
                log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 401

            else:
                error = InternalServerErrorAPI(f'Unexpected error: {response.text}', '', '')
                log('API-get_bearer_token', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 501
