########################################################################################################################
#
# Create customer API call
#
# Date created: 22.02.2021
# Date last modified: 23.02.2021
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
from geoville_ms_database.geoville_ms_database import execute_database, execute_values_database
# from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence
from lib.database_helper import check_processing_unit_exists
from lib.database_helper import get_processing_units_for_spu
from lib.database_helper import check_sup_exists
from lib.database_helper import check_order_id_required
from lib.database_helper import get_order_id_for_tasks
from lib.database_helper import check_production_unit_already_inserted
from models.models_crm.manual_tasks_models.manual_tasks_models import manual_task_request_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_422 import error_422_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import psycopg2
import traceback


########################################################################################################################
# Resource definition for the create customer API call
########################################################################################################################

@api.expect(manual_task_request_model)
@api.header('Content-Type', 'application/json')
class CreateManualTask(Resource):
    """ Class for handling the POST request

    This class defines the API call for the create manual task script. The class consists of one method which accepts a
    POST request. For the POST request a JSON with several parameters is required and defined in the corresponding
    model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', manual_task_request_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(422, 'Unprocessable Entity', error_422_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating a new user

        <p style="text-align: justify">This method defines the handler for the POST request of the create manual task
        script.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This service adds a new manual task entry to the database. In addition to the
        parameters which define a manual task, the service requires a client-id and an access token. As a result the
        service responses the HTTP code 201 combined with the information to further access the manual task entity. If
        an error occurs, the service returns on of the appropriate error status codes (400, 401, 403, 404, 500, 503)</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>processing_unit (list): List with unique processing units)</i></p></li>
        <li><p><i>subproduction_unit (str): Unique subprocessing unit identifier</i></p></li>
        <li><p><i>task_id (str): Unique task identifier</i></p></li>
        <li><p><i>service_id (str): Unique service identifier</i></p></li>
        <li><p><i>comment (str): optional</i></p></li>
        <li><p><i>client_id (str): User client-id</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">SUCCESS: If the entry was added successfully to the database, the service returns
        the HTTP code 201 as well an a dictionary containing two keys (message, links). The value links holds a list of
        all inserted processing_units.</p>
        <p style="text-align: justify">ERROR: In case of an error, the appropriate HTTP error code is returned (400, 401, 403,
        404, 500, 503). Additionally, the service returns a dictionary with two keys (message, error_definition)</p>

        """

        # Get request parameters and check if the payload parameter names are correct
        try:
            req_args = api.payload

            request_processing_unit = None if "processing_unit" not in req_args else req_args['processing_unit']
            request_subproduction_unit = None if "subproduction_unit" not in req_args else req_args[
                'subproduction_unit']

            request_client_id = req_args['client_id']
            # request_service_id = req_args['service_id']
            # request_task_id = req_args['task_id']

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 400

        try:
            # Check if user exists
            if not check_user_existence(request_client_id, database_config_file, database_config_section_api):
                error = UnprocessableEntityError('User ID does not exist', '', '')
                return {'message': error.to_dict()}, 422

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 500

        if request_processing_unit is not None and request_subproduction_unit is not None:
            error = UnprocessableEntityError('Multiple region of interest types are provided. Only one '
                                             'type (processing_unit or subproduction_unit) is supported. ', '', '')
            return {'message': error.to_dict()}, 422

        if request_processing_unit is None and request_subproduction_unit is None:
            error = UnprocessableEntityError('Region of interest (processing_unit, subproduction_unit) is missing', '',
                                             '')
            return {'message': error.to_dict()}, 422

        if request_processing_unit is not None and request_subproduction_unit is None:
            response_dictionary, error_code = self.submit_manual_task_preprocessing_unit(req_args)

        if request_subproduction_unit is not None and request_processing_unit is None:
            response_dictionary, error_code = self.submit_manual_task_spu(req_args)

        return response_dictionary, error_code

    @staticmethod
    def submit_manual_task_preprocessing_unit(req_args):
        """
        This method stores a list of manual tasks based on preprocessing units into the database.
        @param req_args: Request arguments dictionary
        @return: Return a tuple containing the response dictionary and the response code
        """

        try:
            request_processing_unit = req_args['processing_unit']
            request_task_id = req_args['task_id']
            request_service_id = req_args['service_id']
            request_client_id = req_args['client_id']
            # request_status = req_args['status']

            request_comment = None if "comment" not in req_args else req_args['comment']
            # request_result = None if "result" not in req_args else req_args['result']

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 400

        try:
            # Firstly, check if the value for request_processing_unit is from type 'list'
            if not isinstance(request_processing_unit, list):
                error = UnprocessableEntityError('Processing unit value is not from type list'.format(
                    request_processing_unit), '', '')
                return {'message': error.to_dict()}, 422

            # Unique set
            request_processing_unit = list(set(request_processing_unit))

            # Secondly, check if all elements in the list are correct
            incorrect_processing_units = []
            for elem in request_processing_unit:
                processing_unit_exists = check_processing_unit_exists(elem, database_config_file,
                                                                      database_config_section_api)
                if not processing_unit_exists:
                    incorrect_processing_units.append(elem)

            if len(incorrect_processing_units) >= 1:
                error = UnprocessableEntityError('Processing units ({0}) do not exist in database'.format(
                    str(incorrect_processing_units)), '', '')
                return {'message': error.to_dict()}, 422

            # Check if one of the submitted production units was already inserted
            # pu_already_inserted, list_of_pus = check_production_unit_already_inserted(request_processing_unit,
            #                                                                           database_config_file,
            #                                                                           database_config_section_api)
            # if pu_already_inserted:
            #     error = UnprocessableEntityError('Production units already exists in the manual tasks table. List of'
            #                                      'affected units: {0}'.format(list_of_pus), '', '')
            #     return {'message': error.to_dict()}, 422

            # Check if order id is required for the task
            is_order_id_required = check_order_id_required(request_task_id, database_config_file,
                                                           database_config_section_api)

            print("is required: ", is_order_id_required)
            if is_order_id_required:
                # If the order id is required, check ud the order-is is valid. Therefore, get the order-ids for the
                # processing units. If one order-is is missing, an error should be returned

                order_ids_ok, v = get_order_id_for_tasks(request_processing_unit, request_service_id, request_task_id,
                                                         database_config_file, database_config_section_api)
                if not order_ids_ok:
                    incorrect_units = v
                    error = UnprocessableEntityError('The order-id for one or multiple processing units does not exist '
                                                     'in the database - affected units: {0}'
                                                     .format(incorrect_units), '', '')
                    return {'message': error.to_dict()}, 422
                else:
                    order_ids = v

            # Insert the manual task into the database
            for element in request_processing_unit:
                task_started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                state_running = "RUNNING"

                if is_order_id_required:
                    refers_to_order_id = order_ids[element]
                else:
                    refers_to_order_id = None

                print(refers_to_order_id)

                values = (
                    element, request_client_id, request_service_id, request_task_id, task_started, None,
                    state_running, None, None, refers_to_order_id, request_comment
                )

                sql = """
                    INSERT INTO customer.manual_tasks
                    (
                        cell_code, customer_id, service_id, task_id, task_started, task_stopped, status,  "result", 
                        deleted_at, refers_to_order_id, "comment"
                    ) 
                    VALUES
                    (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """

                try:
                    execute_database(sql, values, database_config_file, database_config_section_api, True)
                except Exception:
                    error = InternalServerErrorAPI(f'Unexpected error occurred for unit {element}',
                                                   api.payload,
                                                   traceback.format_exc())
                    return {'message': error.to_dict()}, 500

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 500

        # Create final response
        response_links = []
        for element in request_processing_unit:
            d = {
                'href': f'/crm/manual_tasks/task_query?processing_unit={element}',
                'rel': 'manual_tasks',
                'type': 'GET'
            }
            response_links.append(d)

        response = {
            'message': 'Your order has been successfully submitted',
            'links': response_links
        }

        return response, 200

    @staticmethod
    def submit_manual_task_spu(req_args):
        """
        This method stores a manual tasks based on a subproduction unit into the database.
        @param req_args: Request arguments dictionary
        @return: Return a tuple containing the response dictionary and the response code
        """

        # Get the request parameters and set default values for missing values
        try:
            request_subproduction_units = req_args['subproduction_unit']
            request_task_id = req_args['task_id']
            request_service_id = req_args['service_id']
            request_client_id = req_args['client_id']

            request_comment = None if "comment" not in req_args else req_args['comment']

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 400

        try:

            for request_subproduction_unit in request_subproduction_units:
                # Check if sup exists and retrieve a list of all processing units for the subproduction unit
                sup_exists = check_sup_exists(request_subproduction_unit, database_config_file,
                                              database_config_section_api)

                if not sup_exists:
                    error = UnprocessableEntityError('Subproduction unit ({0}) does not exist in database'.format(
                        request_subproduction_unit), '', '')
                    return {'message': error.to_dict()}, 422

                # Get a list of all processing units for the subproduction unit
                processing_units = get_processing_units_for_spu(request_subproduction_unit, database_config_file,
                                                                database_config_section_api)

                # Unique set
                processing_units = list(set(processing_units))

                # Check if one of the submitted production units was already inserted
                # pu_already_inserted, list_of_pus = check_production_unit_already_inserted(processing_units,
                #                                                                           database_config_file,
                #                                                                           database_config_section_api)
                # if pu_already_inserted:
                #     error = UnprocessableEntityError('Production units already exists in the manual tasks table. List of'
                #                                      'affected units: {0}'.format(list_of_pus), '', '')
                #     return {'message': error.to_dict()}, 422

                # Check if order-id is required for the task
                is_order_id_required = check_order_id_required(request_task_id, database_config_file,
                                                               database_config_section_api)
                if is_order_id_required:
                    # If the order id is required, check if the order-is is valid. Therefore, get the order-ids for the
                    # processing units. If one order-is is missing, an error should be returned

                    order_ids_ok, v = get_order_id_for_tasks(processing_units, request_service_id, request_task_id,
                                                             database_config_file, database_config_section_api)
                    if not order_ids_ok:
                        incorrect_units = v
                        error = UnprocessableEntityError('The order-id for one or multiple processing units does not exist '
                                                         'in the database - affected unis: {0}'
                                                         .format(incorrect_units), '', '')
                        return {'message': error.to_dict()}, 422
                    else:
                        order_ids = v

                # Insert the manual task (based on processing_unit) into the database
                for element in processing_units:
                    task_started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    state_running = "RUNNING"

                    if is_order_id_required:
                        refers_to_order_id = order_ids[element]
                    else:
                        refers_to_order_id = None

                    values = (
                        element, request_client_id, request_service_id, request_task_id, task_started,
                        state_running, refers_to_order_id, request_comment
                    )

                    sql = """
                        INSERT INTO customer.manual_tasks
                        (
                            cell_code, customer_id, service_id, task_id, task_started, status, 
                            refers_to_order_id, comment
                        ) 
                        VALUES 
                        (%s, %s,%s,%s,%s,%s,%s, %s)
                    """

                    try:
                        execute_database(sql, values, database_config_file, database_config_section_api, True)

                    except psycopg2.errors.UniqueViolation as err:
                        error = BadRequestError(
                            f'Unique Key constraint {element}: {err}',
                            api.payload,
                            traceback.format_exc())
                        return {'message': error.to_dict()}, 400

                    except Exception as err:
                        error = InternalServerErrorAPI(
                            f'Unexpected error occurred for unit {element}: {err}',
                            api.payload,
                            traceback.format_exc())
                        return {'message': error.to_dict()}, 500

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            return {'message': error.to_dict()}, 503

        except Exception as err:
            error = InternalServerErrorAPI(f'Unexpected error occurred: {err}', api.payload, traceback.format_exc())
            return {'message': error.to_dict()}, 500

        # Create final response
        response_links = []
        for element in processing_units:
            d = {
                'href': f'/crm/manual_tasks/task_query?processing_unit={element}',
                'rel': 'manual_tasks',
                'type': 'GET'
            }
            response_links.append(d)

        response = {
            'message': 'Your order has been successfully submitted',
            'links': response_links
        }

        return response, 200


