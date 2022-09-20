########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
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
# __version__ = 21.02
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
from models.models_crm.manual_tasks_models.manual_tasks_models import manual_task_update_state_response_model
from models.models_crm.manual_tasks_models.manual_tasks_models import manual_task_update_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_422 import error_422_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback
import datetime

########################################################################################################################
# Resource definition for the update state API call
########################################################################################################################

@api.expect(manual_task_update_model)
@api.header('Content-Type', 'application/json')
class UpdateManualTask(Resource):
    """ Class for handling the PUT request

    This class defines the API call for the update manual task script. The class consists of one method which accepts a
    PUT request. For the PUT request a JSON with several parameters is required and defined in the corresponding
    model.

    """

    ####################################################################################################################
    # Method for handling the PUT request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', manual_task_update_state_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Unprocessable Entity', error_422_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def put(self):
        """ PUT definition for update a manual task

        <p style="text-align: justify">This method defines the handler for the PUT request of the update manual task
        (sate and result) script.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This service updates an existing manual task entry in the database. The put
        request is used to update the <i>state</i> column in the database. If the results value is <i>finished</i>,
        the <i>result</i> key is also required. As a result the service responses the HTTP code 201. If an error occurs,
        the service returns one of the appropriate error status codes (400, 401, 403, 404, 500, 503)</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>state (str): New state for the task (not_started, in_progress, failed, finished)</i></p></li>
        <li><p><i>result (str): Result for the task (required when state='finished')</i></p></li>
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

            request_state = req_args['state']
            request_processing_unit = req_args['processing_unit']
            request_service_id = req_args['service_id']
            request_task_id = req_args['task_id']
            request_client_id = req_args['client_id']
            request_result = None if "result" not in req_args else req_args['result']

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 400

        try:
            # Validate user existence
            if not check_user_existence(request_client_id, database_config_file, database_config_section_api):
                error = UnprocessableEntityError('User ID does not exist', '', '')
                return {'message': error.to_dict()}, 422

            # Check if status value is correct
            supported_state_values = {"not_started": None, "in_progress": "RUNNING", "failed": "FAILED",
                                      "finished": "SUCCESS"}

            if request_state.lower() not in supported_state_values:
                error = UnprocessableEntityError('Status ({0}) is not supported'.format(request_state), '', '')
                return {'message': error.to_dict()}, 422

            if request_state.lower() == "finished":
                if not request_result:
                    error = UnprocessableEntityError('Result missing - value for result can not be NULL when state is '
                                                     'finished'.format(request_state), '', '')
                    return {'message': error.to_dict()}, 422

                sql = """
                    UPDATE customer.manual_tasks 
                    SET    status = %s,
                           "result" = %s,
                           task_stopped = %s
                    WHERE  ( cell_code = %s 
                             AND service_id = %s
                             AND task_id = %s ); 
                """
                task_stopped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task_state = supported_state_values[request_state]

                parameter_tuple = (task_state, request_result, task_stopped, request_processing_unit,
                                   request_service_id, request_task_id, )
                execute_database(sql, parameter_tuple, database_config_file, database_config_section_api, True)

            else:
                sql = """
                    UPDATE customer.manual_tasks 
                    SET    status = %s,
                           "result" = %s,
                           task_stopped = %s
                    WHERE  ( cell_code = %s 
                             AND service_id = %s
                             AND task_id = %s ); 
                """

                task_state = supported_state_values[request_state]
                parameter_tuple = (task_state, None, None, request_processing_unit, request_service_id, request_task_id,)
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
            }

            return response, 200




