########################################################################################################################
#
# Adds a new Airflow configuration to the database
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
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import config_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_airflow_service_existence
from models.models_config.airflow_models.airflow_config_models import add_airflow_config_model, airflow_config_success_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_404 import error_404_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the inserting a new Airflow configuration API call
########################################################################################################################

@api.expect(add_airflow_config_model)
@api.header('Content-Type', 'application/json')
class AddAirflowConfig(Resource):
    """ Class for handling the POST request

    This class defines the API call for the add Airflow configuration script. The class consists of one method which
    accepts a POST request. For the POST request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', airflow_config_success_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for adding a new Airflow configuration

        <p style="text-align: justify">This method defines the handler for the POST request of the add Airflow
        configuration script. It returns a message wrapped into a dictionary about the status of the insertion
        operation.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>service_name (str): Full name of the client</i></p></li>
        <li><p><i>command (str): Full name of the client</i></p></li>
        <li><p><i>description (str): Full name of the client</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        try:
            req_args = api.payload
            gemslog(LogLevel.INFO, f'Request: {req_args}', 'API-add_airflow_config')

            if check_airflow_service_existence(req_args['service_name'], database_config_file, database_config_section_api):
                error = NotFoundError('Service name exists already', '', '')
                gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-add_airflow_config')
                return {'message': error.to_dict()}, 404

            db_query = """INSERT INTO msgeovilleconfig.airflow_config
                          ( 
                              service_name, command, description
                          ) 
                          VALUES
                          (
                              %s, %s, %s
                          )
                       """

            execute_database(db_query, (req_args['service_name'], req_args['command'], req_args['description']),
                             database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-add_airflow_config')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-add_airflow_config')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-add_airflow_config')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Request: {req_args}', 'API-add_airflow_config')
            return {'service_name': req_args['service_name']}, 201
