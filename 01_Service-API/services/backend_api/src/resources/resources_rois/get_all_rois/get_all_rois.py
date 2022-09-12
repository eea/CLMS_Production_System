########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get all regions of interest API call
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
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from models.models_rois.roi_models import several_roi_response_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import json
import traceback


########################################################################################################################
# Resource definition for the get all regions of interest API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class GetAllROIs(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get all regions of interest script. The class consists of one method which
    accepts a GET request. For the GET request no parameters are required.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation successful', several_roi_response_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self):
        """ GET definition for retrieving all regions of interest

        <p style="text-align: justify">This method defines the handler for the GET request of the get all regions of
        interest script. It returns a list of regions of interest of all data sets in the database if the required table
        is not empty.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This GEMS service provides an overview of all stored region of interests in the
        database belonging to a GEMS customer. By specifying the customer ID all the available region of interests will
        be returned and listed in an detailed manner with all the parameters submitted in the creation process.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON </p>

        """

        db_query = """SELECT 
                          roi_id, roi_name, description, user_id, ST_AsGeoJSON(geom), created_at
                      FROM 
                          clcplus_users.region_of_interests;
                   """

        try:
            roi_data = read_from_database_all_rows(db_query, (), database_config_file, database_config_section_api, True)
            res_array = []

            for roi in roi_data:
                roi_obj = {
                    'roi_id': roi[0],
                    'roi_name': roi[1],
                    'description': roi[2],
                    'user_id': roi[3],
                    'geoJSON': json.loads(roi[4]),
                    'creation_date': roi[5].strftime("%Y-%m-%dT%H:%M:%S")
                }

                res_array.append(roi_obj)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-get_all_rois', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_all_rois', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-get_all_rois', LogLevel.INFO, f'Successful response: {res_array}')
            return {'rois': res_array}, 200
