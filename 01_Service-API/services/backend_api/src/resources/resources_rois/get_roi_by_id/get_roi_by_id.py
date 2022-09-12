########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get region of interest by ID API call
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.http_error_400.http_error_400 import BadRequestError
from error_classes.http_error_404.http_error_404 import NotFoundError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import read_from_database_one_row
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_roi_existence
from models.models_rois.roi_models import single_roi_response_model
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
# Resource definition for the get region of interest by ID API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('roi_id', 'ROI ID to be deleted')
class GetROIByID(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get region of interest by ID script. The class consists of one method which
    accepts a GET request. For the GET request a JSON with one parameter is required and defined in the corresponding
    model.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.doc(parser=auth_header_parser)
    @api.response(200, 'Operation successful', single_roi_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, roi_id):
        """ GET definition for retrieving a region of interest by ID

        <p style="text-align: justify">This method defines the handler for the GET request of the get region of interest
        by ID script. It returns the region of interest for the given ID if it exists in the database.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This GEMS service provides an overview of all stored region of interests in the
        database belonging to a GEMS customer. By specifying the customer ID all the available region of interests will
        be returned and listed in an detailed manner with all the parameters submitted in the creation process.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Path parameters:</b>
        <ul>
        <li><p><i>roi_id (str): Unique identifier for the region of interest</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON</p>

        """

        db_query = """SELECT 
                          roi_id, roi_name, description, user_id, ST_AsGeoJSON(geom), created_at
                      FROM 
                          clcplus_users.region_of_interests 
                      WHERE 
                          roi_id = %s;
                   """

        try:
            log('API-get_roi_by_id', LogLevel.INFO, f'Request path parameter: {roi_id}')

            if not check_roi_existence(roi_id, database_config_file, database_config_section_api):
                error = NotFoundError('ROI ID does not exist', '', '')
                log('API-get_roi_by_id', LogLevel.WARNING, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 404

            roi_data = read_from_database_one_row(db_query, (roi_id,), database_config_file,
                                                  database_config_section_api, True)

            roi_obj = {
                'roi_id': roi_data[0],
                'roi_name': roi_data[1],
                'description': roi_data[2],
                'user_id': roi_data[3],
                'geoJSON': json.loads(roi_data[4]),
                'creation_date': str(roi_data[5])
            }

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-get_roi_by_id', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-get_roi_by_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-get_roi_by_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-get_roi_by_id', LogLevel.INFO, f'Successful response: {roi_obj}')
            return roi_obj, 200
