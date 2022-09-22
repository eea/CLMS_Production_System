########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Set OAuth2 token expiration time API call
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
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_oauth
from init.namespace_constructor import auth_namespace as api
from lib.auth_header import auth_header_parser
from models.models_auth.token_models.token_models import exp_time_request_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the set OAuth2 token expiration time API call
########################################################################################################################

@api.expect(exp_time_request_model)
@api.header('Content-Type', 'application/json')
class UpdateTokenExpirationTime(Resource):
    """ Class for handling the PATCH request

    This class defines the API call for the set OAuth 2 token expiration time script. The class consists of one method which
    accepts a PATCH request. For the PATCH request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the PATCH request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(204, 'Operation successful')
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def patch(self):
        """ PATCH definition for setting the OAuth2 token expiration time

        <p style="text-align: justify">This method defines the handler for the PATCH request of the set OAuth2 token
        expiration time script. It returns a no message about the status of the update operation. In contrast it returns
        the HTTP status code 204.</p>

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
        <p style="text-align: justify">The result of the PATCH request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicated an error during the execution.</p>

        """

        try:
            req_args = api.payload
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-token_time')

            db_query = """UPDATE 
                                          public.oauth2_token 
                                      SET 
                                          expires_in = %s, 
                                          updated_at = NOW() 
                                      WHERE 
                                          access_token = %s AND
                                          deleted_at IS NULL
                                   """
            execute_database(db_query, (req_args['exp_time'], req_args['bearer_token']), database_config_file,
                             database_config_section_oauth, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-token_time')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-token_time')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-token_time')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, 'Set new token expiration time', 'API-token_time')
            return '', 204



