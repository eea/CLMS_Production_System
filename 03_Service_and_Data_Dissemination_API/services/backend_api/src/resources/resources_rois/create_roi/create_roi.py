########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Create region of interest API call
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
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence
from lib.general_helper_methods import validate_geojson
from lib.hashing_helper import generate_roi_id_hash
from models.models_rois.roi_models import roi_id_model, roi_request_model
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
# Resource definition for the create region of interest API call
########################################################################################################################

@api.expect(roi_request_model)
@api.header('Content-Type', 'application/json')
class CreateROI(Resource):
    """ Class for handling the POST request

    This class defines the API call for the create  region of interest script. The class consists of one method which
    accepts a POST request. For the POST request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(201, 'Operation successful', roi_id_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating a new region of interest

        <p style="text-align: justify">This method defines the handler for the POST request of the create region of
        interest script. It returns a message wrapped into a dictionary about the status of the insertion operation.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">Most of the GEMS services work with an area of interest as input parameter. For
        this, the GEMS API offers the consumer the possibility to create his own area of interest. In the GEMS concept,
        it is called region of interest. Each API consumer can create as many region of interests as necessary.</p>


        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>name (str): Name identifier for the region of interest</i></p></li>
        <li><p><i>description (str): Longer description for the region of interest but not required</i></p></li>
        <li><p><i>user_id (str): User specific client ID to link the region of interst to a user</i></p></li>
        <li><p><i>geoJSON (str): GeoJSON definition of the region of interest without any additional attributes</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON which contains an object with one key
        value pair. The region of interest ID is required as input parameter for several GEMS services and should not be
        lost.</p>
        <ul>
        <li><p><i>roi_id: Unique identifier of a region of interest</i></p></li>
        </ul>

        """

        try:
            req_args = api.payload
            gemslog(LogLevel.INFO, f'Request payload: {req_args}', 'API-create_roi')

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_roi')
                return {'message': error.to_dict()}, 404

            validation_res = validate_geojson(req_args['geoJSON'], database_config_file, database_config_section_api)
            if False in validation_res:
                error = BadRequestError(f'GeoJSON is invalid: {validation_res[1]}', api.payload, '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_roi')
                return {'message': error.to_dict()}, 400

            description = None if 'description' not in req_args else req_args['description']
            roi_id = generate_roi_id_hash(req_args['user_id'], req_args['name'])

            db_query = """INSERT INTO customer.region_of_interests
                          ( 
                              roi_id, roi_name, description, customer_id, geom
                          ) 
                          VALUES
                          (
                              %s, %s, %s, %s, ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                          )
                       """

            execute_database(db_query, (roi_id, req_args['name'], description, req_args['user_id'],
                                        json.dumps(req_args['geoJSON'])), database_config_file,
                             database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-create_roi')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_roi')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-create_roi')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Created ROI with ID: {roi_id}', 'API-create_roi')
            return {'roi_id': roi_id}, 201
