########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create service API call
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
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_service_name_existence
from lib.hashing_helper import generate_service_id_hash
from models.models_crm.service_models.service_models import service_creation_model, service_id_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the create customer API call
########################################################################################################################

@api.expect(service_creation_model)
@api.header('Content-Type', 'application/json')
class CreateService(Resource):
    """ Class for handling the POST request

    This class defines the API call for the create customer script. The class consists of one method which accepts a
    POST request. For the POST request a JSON with several parameters is required and defined in the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', service_id_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating a new service

        <p style="text-align: justify">This method defines the handler for the POST request of the create service
        script. It returns a message wrapped into a dictionary about the process of the insertion operation.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>service_name (str): </i></p></li>
        <li><p><i>service_validity (str): </i></p></li>
        <li><p><i>service_owner_geoville (str): </i></p></li>
        <li><p><i>service_comment (str): </i></p></li>
        <li><p><i>external (str): </i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        try:
            req_args = api.payload
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-create_service')

            if check_service_name_existence(req_args['service_name'], database_config_file, database_config_section_api):
                error = BadRequestError('Service name exists already', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_service')
                return {'message': error.to_dict()}, 400

            service_comment = None if 'service_comment' not in req_args else req_args['service_comment']
            service_id = generate_service_id_hash(req_args['service_name'], req_args['service_owner_geoville'])

            db_query = """INSERT INTO customer.services
                          ( 
                            service_id, service_name, service_validity, service_owner_geoville, service_comment, external
                          ) 
                          VALUES
                          (
                            %s, %s, %s, %s, %s, %s
                          );
                       """

            execute_database(db_query, (service_id, req_args['service_name'], req_args['service_validity'],
                                        req_args['service_owner_geoville'], service_comment, req_args['external']),
                             database_config_file, database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_service')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_service')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_service')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, 'Successfully created new service', 'API-create_service')
            return {'service_id': service_id}, 201
