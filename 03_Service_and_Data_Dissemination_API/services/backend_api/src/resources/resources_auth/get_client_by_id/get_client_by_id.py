########################################################################################################################
#
# Get OAuth2 client by ID API call
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
from init.init_env_variables import database_config_file, database_config_section_oauth
from init.namespace_constructor import auth_namespace as api
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from lib.auth_header import auth_header_parser
from lib.database_helper import check_client_id_existence
from models.models_auth.client_models.client_models import client_response_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the get OAuth2 client by ID API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('user_id', 'User ID to be requested')
class GetClientByID(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get OAuth2 client by ID script. The class consists of one method which accepts a
    GET request. For the GET request an additional path parameter is required..

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', client_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, user_id):
        """ GET definition for retrieving an OAuth2 client by ID

        <p style="text-align: justify">This method defines the handler for the GET request of the get OAuth2 client by
        ID script. It returns a message wrapped into a dictionary with all the necessary client information.</p>

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
            if not check_client_id_existence(user_id, database_config_file, database_config_section_oauth):
                error = NotFoundError('Client ID does not exist', '', '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_client_by_id')
                return {'message': error.to_dict()}, 404

            db_query = """SELECT 
                              client_id, client_metadata 
                          FROM 
                              public.oauth2_client 
                          WHERE 
                              client_id = %s AND
                              deleted_at IS NULL
                       """

            client_data = read_from_database_one_row(db_query, (user_id,), database_config_file,
                                                     database_config_section_oauth, True)
            additional_data = json.loads(client_data[1]) if client_data is not None else None

            client_obj = {'client_id': client_data[0],
                          'client_name': additional_data['client_name'],
                          'grant_type': additional_data['grant_types'],
                          'response_type': additional_data['response_types'],
                          'scope': additional_data['scope']
                          } if client_data is not None else {}

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', '', traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_client_by_id')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_client_by_id')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', '', traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_client_by_id')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, 'Request successful', 'API-get_client_by_id')
            return client_obj, 200
