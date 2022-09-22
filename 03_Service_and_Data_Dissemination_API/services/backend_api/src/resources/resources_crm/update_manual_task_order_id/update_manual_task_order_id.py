########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create customer API call
#
# Date created: 22.02.2021
# Date last modified: 04.03.2021
#
# __author__  = Patrick Wolf (wolf@geoville.com)
# __version__ = 21.03
#
########################################################################################################################

import datetime
from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_422.http_error_422 import UnprocessableEntityError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence
from models.models_crm.manual_tasks_models.manual_tasks_models import manual_task_update_order_id_model
from models.models_crm.manual_tasks_models.manual_tasks_models import manual_task__update_order_id_response_model
from lib.database_helper import check_order_id_exists
from lib.database_helper import check_state_is_success
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_422 import error_422_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback

########################################################################################################################
# Resource definition for the update order_id API call
########################################################################################################################

@api.expect(manual_task_update_order_id_model)
@api.header('Content-Type', 'application/json')
class UpdateManualTaskOrderID(Resource):
    """ Class for handling the PUT request

    This class defines the API call for the update manual task (order-id) script. The class consists of one method
    which accepts a PUT request. For the PUT request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the PUT request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', manual_task__update_order_id_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Unprocessable Entity', error_422_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def put(self):
        """ PUT definition for update a manual task

        <p style="text-align: justify">This method defines the handler for the PUT request of the update manual task
        (order_id) script.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This service updates an existing manual task entry in the database. The put
        request is used to update the <i>refers_to_order_id</i> column in the database. As a result the service
        responses the HTTP code 201. If an error occurs, the service returns one of the appropriate error status
        codes (400, 401, 403, 404, 500, 503)</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>refers_to_order_id (str): New order-id value</i></p></li>
        <li><p><i>processing_unit (str): Unique processing unit identifier</i></p></li>
        <li><p><i>service_id (str): Unique service identifier</i></p></li>
        <li><p><i>task_id (str): Unique task identifier</i></p></li>
        <li><p><i>client_id (str): User client-id</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">SUCCESS: If the entry was updated successfully in the database, the service
        returns the HTTP code 204 as well an a dictionary containing the key message.</p>
        <p style="text-align: justify">ERROR: In case of an error, the appropriate HTTP error code is returned (400,
        401, 403, 404, 500, 503). Additionally, the service returns a dictionary with two keys
        (message, error_definition)</p>

        """

        # Get request parameters and check if the payload parameter names are correct
        try:
            req_args = api.payload

            request_refers_to_order_id = req_args['refers_to_order_id']
            request_processing_unit = req_args['processing_unit']
            request_service_id = req_args['service_id']
            request_task_id = req_args['task_id']
            request_client_id = req_args['client_id']

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 400

        try:
            # Validate user existence
            if not check_user_existence(request_client_id, database_config_file, database_config_section_api):
                error = UnprocessableEntityError('User ID does not exist', '', '')
                return {'message': error.to_dict()}, 422

            # Check if order-id exists
            refers_to_order_id_exists = check_order_id_exists(request_refers_to_order_id, database_config_file,
                                                              database_config_section_api)
            if not refers_to_order_id_exists:
                error = UnprocessableEntityError('Order-ID ({0}) does not exist'.format(request_refers_to_order_id), '', '')
                return {'message': error.to_dict()}, 422

            # Check if state is correct
            is_success = check_state_is_success(request_processing_unit, request_service_id, request_task_id,
                                                database_config_file, database_config_section_api)
            if not is_success:
                error = UnprocessableEntityError('Could not update refers_to_order_id - state is not SUCCESS or '
                                                 'database entity (task, service, processing_unit) does not exist'.
                                                 format(request_refers_to_order_id), '', '')
                return {'message': error.to_dict()}, 422

            # Update the refers_to_order_id column
            sql = """
                update
                    customer.manual_tasks
                set
                    refers_to_order_id = %s
                where
                    cell_code = %s
                    and service_id = %s
                    and task_id = %s ;
            """
            parameter_tuple = (request_refers_to_order_id, request_processing_unit, request_service_id, request_task_id,)
            execute_database(sql, parameter_tuple, database_config_file, database_config_section_api, True)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 500

        else:
            response = {
                'message': 'Your update has been successfully submitted',
                'refers_to_order_id': request_refers_to_order_id
            }
            return response, 200




