########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get service by name API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_service_name_existence
from models.models_crm.service_models.service_models import service_object_model
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resources definition for the get service by name API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('service_name', 'Service name to be requested')
class GetServiceByName(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get service by name script. The class consists of one method which accepts a
    GET request. For the GET request an additional path parameter is required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation was successful', service_object_model)
    @api.response(400, 'Bad Request', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, service_name):
        """ GET definition for retrieving a service by name

        <p style="text-align: justify">This method defines the handler for the GET request of the get service by name
        script. It returns all service data stored in the database wrapped into a dictionary defined by corresponding
        model.</p>

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

        db_query = """SELECT
                          service_id, service_name, service_comment, service_validity, service_owner_geoville, 
                          external, created_at
                      FROM 
                          customer.services
                      WHERE
                          service_name = %s
                   """

        try:
            log('API-get_service_by_name', LogLevel.INFO, f'Request path parameter: {service_name}')

            if not check_service_name_existence(service_name, database_config_file, database_config_section_api):
                error = BadRequestError('Service name does not exist', '', '')
                log('API-get_service_by_name', LogLevel.WARNING, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 400

            service_data = read_from_database_one_row(db_query, (service_name, ), database_config_file,
                                                      database_config_section_api, True)

            service_obj = {
                'service_id': service_data[0],
                'service_name': service_data[1],
                'service_comment': service_data[2],
                'service_validity': service_data[3],
                'service_owner_geoville': service_data[4],
                'external': service_data[5],
                'date_of_creation': service_data[6].strftime("%Y-%m-%dT%H:%M:%S")
            }

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-get_service_by_name', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_service_by_name', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-get_service_by_name', LogLevel.INFO, f'Successful response')
            return service_obj, 200
