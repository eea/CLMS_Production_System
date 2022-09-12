########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Update region of interest API call
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
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_roi_existence, check_user_existence
from lib.general_helper_methods import validate_geojson
from models.models_rois.roi_models import roi_entity_request
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
# Resource definition for the create customer API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class UpdateROIEntity(Resource):
    """ Class for handling the PUT request

    This class defines the API call for the update region of interest script. The class consists of one method which
    accepts a PUT request. For the PUT request a JSON with several parameters is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the PUT request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.doc(body=roi_entity_request, parser=auth_header_parser)
    @api.response(204, 'Operation successful')
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def put(self):
        """ PUT definition for updating a complete region of interest entity

        <p style="text-align: justify">This method defines the handler for the PUT request of the update region of
        interest script. It returns a message wrapped into a dictionary about the status of the update operation.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This GEMS service was designed to quickly update a single or a couple of
        attributes of a region of interest without submitting attributes which should not be changed, that's why some
        attributes can be submitted as optional parameters. As common use in API design, all PATCH request will not
        provide any return message from service. Only the HTTP status code should be checked for retrieving the result
        of the request.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>roi_id (str): Unique identifier for a region of interest</i></p></li>
        <li><p><i>name (str): Name identifier for the region of interest</i></p></li>
        <li><p><i>description (str): Longer description for the region of interest but not required</i></p></li>
        <li><p><i>customer_id (str): User specific client ID to link the region of interst to a user</i></p></li>
        <li><p><i>geoJSON (str): GeoJSON definition of the region of interest without any additional attributes</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the PUT request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicated an error during the execution.</p>

        """

        try:
            req_args = api.payload
            log('API-update_roi_entity_by_id', LogLevel.INFO, f'Request payload: {req_args}')

            if not check_roi_existence(req_args['roi_id'], database_config_file, database_config_section_api):
                error = NotFoundError('ROI ID does not exist', '', '')
                log('API-update_roi_entity_by_id', LogLevel.WARNING, 'ROI ID does not exist')
                return {'message': error.to_dict()}, 404

            if not check_user_existence(req_args['user_id'], database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                log('API-update_roi_entity_by_id', LogLevel.WARNING, 'Customer ID does not exist')
                return {'message': error.to_dict()}, 404

            validation_res = validate_geojson(req_args['geoJSON'], database_config_file, database_config_section_api)
            if False in validation_res:
                error = BadRequestError(f'GeoJSON is invalid: {validation_res[1]}', api.payload, '')
                log('API-create_roi', LogLevel.WARNING, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 400

            description = None if 'description' not in req_args else req_args['description']

            db_query = """UPDATE 
                              clcplus_users.region_of_interests
                          SET 
                              roi_name = %s, 
                              description = %s, 
                              user_id = %s, 
                              geom = ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                          WHERE 
                              roi_id = %s;
                       """

            execute_database(db_query, (req_args['name'], description, req_args['user_id'],
                                        json.dumps(req_args['geoJSON']), req_args['roi_id']), database_config_file,
                             database_config_section_api, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-update_roi_entity_by_id', LogLevel.WARNING, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-update_roi_entity_by_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-update_roi_entity_by_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-update_roi_entity_by_id', LogLevel.INFO, 'Updated ROI successfully')
            return '', 204
