########################################################################################################################
#
# Login API Call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_408.http_error_408 import RequestTimeoutError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from flask_restx import Resource
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.app_constructor import bcrypt
from init.init_env_variables import (database_config_file, database_config_section_api, database_config_section_oauth)
from init.namespace_constructor import auth_namespace as api
from lib.database_helper import (check_email_existence, get_client_id_secret)
from lib.request_helper import get_bearer_token
from models.models_auth.login_model.login_model import login_request_model, login_response_model
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
# Resource definition for the get bearer token API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class Login(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get Bearer token script. The class consists of one method which accepts a
    GET request. For the GET request two path parameters are required.
    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @api.expect(login_request_model)
    @api.response(200, 'Operation successful', login_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(408, 'Request Timeout', error_408_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for logging in

        <p style="text-align: justify">This method defines the handler for the GET request of the get Bearer token
        request. It returns all the information from the OAuth2 server</p>

        <br><b>Description:</b>
        <p style="text-align: justify">The GEMS microservice architecture has foreseen an OAuth2 authentication and
        authorisation server for handling the GEMS costumers login and the access to GEMS services. To gain access of
        the services of the GEMS API it is necessary for each consumer to create login and gain a new Bearer token from
        this service route. The token type and the token itself are needed for service routes which require an
        authorisation header. In the authorisation header, the API consumer need to write the token in the following
        format "Bearer XXXX".</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>None</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>email (str): User specific client ID provided by the GEMS administration team</i></p></li>
        <li><p><i>password (str): User specific client secret provided by the GEMS administration team</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the submitted request is an automatically created JSON response of
        the OAuth2 server which returns the following parameters:</p>
        <ul>
        <li><p><i>access_token: Token needed for all the authorisation steps</i></p></li>
        <li><p><i>expires_in: Expiration time of the token in seconds</i></p></li>
        <li><p><i>refresh_token: Can be used to obtain a renewed access token</i></p></li>
        <li><p><i>scope: All grants the specific user has</i></p></li>
        <li><p><i>token_type: Type of the token, in case of GEMS, it is always Bearer. Needed in the authorisation header</i></p></li>
        </ul>

        """

        try:
            req_args = api.payload

            user_id = check_email_existence(req_args['email'], database_config_file, database_config_section_api)
            if not user_id:
                error = BadRequestError(f'User does not exist', api.payload, '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
                return {'message': error.to_dict()}, 400

            if not bcrypt.check_password_hash(user_id[1], req_args['password']):
                error = BadRequestError(f'Wrong password submitted', api.payload, '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
                return {'message': error.to_dict()}, 400

            client_secret = get_client_id_secret(user_id[0], database_config_file, database_config_section_oauth)
            token_response = get_bearer_token(user_id[0], client_secret)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', '', traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
            return {'message': error.to_dict()}, 400

        except requests.exceptions.ReadTimeout:
            error = RequestTimeoutError('Connection timed out while contacting the Authorization server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
            return {'message': error.to_dict()}, 408

        except HTTPError:
            error = NotFoundError(f'Could not connect to OAuth2 server', '', traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
            return {'message': error.to_dict()}, 404

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-login')
            return {'message': error.to_dict()}, 500

        else:
            token_response.update([('client_id', user_id[0]), ('client_secret', client_secret)])
            gemslog(LogLevel.INFO, 'Login successful', 'API-login')
            return token_response
