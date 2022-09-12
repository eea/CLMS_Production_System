########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get all services API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import crm_namespace as api
from lib.auth_header import auth_header_parser
from models.models_crm.service_models.service_models import service_list_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resources definition for the get all services API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetAllServices(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get all services script. The class consists of one method which accepts a
    GET request. For the GET request no additional parameter are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation was successful', service_list_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving all services

        <p style="text-align: justify">This method defines the handler for the GET request of the get all services
        script. It returns all service data stored in the database wrapped into a dictionary defined by corresponding
        model.</p>

        <br><b>Description:</b>
        <p style="text-align: justify"></p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify"></p>

        """

        db_query = """SELECT
                          service_id, service_name, service_comment, service_validity, service_owner_geoville, 
                          external, created_at
                      FROM 
                          customer.services
                   """

        try:
            service_data = read_from_database_all_rows(db_query, (), database_config_file, database_config_section_api,
                                                       True)
            res_array = []

            for service in service_data:
                service_obj = {
                    'service_id': service[0],
                    'service_name': service[1],
                    'service_comment': service[2],
                    'service_validity': service[3],
                    'service_owner_geoville': service[4],
                    'external': service[5],
                    'date_of_creation': service[6].strftime("%Y-%m-%dT%H:%M:%S")
                }

                res_array.append(service_obj)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-get_services', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_services', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-get_services', LogLevel.INFO, f'Successfully queried all services')
            return {'services': res_array}, 200
