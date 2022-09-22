########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get region of interest by ID API call
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
from geoville_ms_database.geoville_ms_database import read_from_database_all_rows
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from lib.database_helper import check_user_existence
from models.models_rois.roi_models import several_roi_response_model
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
@api.param('user_id', 'User ID to be deleted')
class GetROIByUserID(Resource):
    """ Class for handling the GET request

    This class defines the API call for the get region of interest by ID script. The class consists of one method which
    accepts a GET request. For the GET request a JSON with one parameter is required
    and defined in the corresponding model.

    """

    ####################################################################################################################
    # Method for handling the GET request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.expect(auth_header_parser)
    @api.response(200, 'Operation successful', several_roi_response_model)
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(404, 'Not Found Error', error_404_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def get(self, user_id):
        """ GET definition for retrieving a region of interest by user ID

        <p style="text-align: justify">This method defines the handler for the GET request of the get region of interest
        by user ID script. It returns the region of interest for the given ID if it exists in the database.</p>

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
        <li><p><i>customer_id (str): Unique identifier for a GEMS customer</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the GET request is a JSON which contains a list of objects with
        four key value pairs. Those pairs are conform with the parameters submitted during the region of interest
        creation</p>
        <ul>
        <li><p><i>name</i></p></li>
        <li><p><i>description</i></p></li>
        <li><p><i>customer_id</i></p></li>
        <li><p><i>geoJSON</i></p></li>
        </ul>

        """

        db_query = """SELECT 
                          roi_id, roi_name, description, customer_id, ST_AsGeoJSON(geom), created_at
                      FROM 
                          customer.region_of_interests 
                      WHERE 
                          customer_id = %s AND
                          deleted_at IS NULL;
                   """

        try:
            gemslog(LogLevel.INFO, f'Request path parameter: {user_id}', 'API-get_roi_by_user')

            if not check_user_existence(user_id, database_config_file, database_config_section_api):
                error = NotFoundError('User ID does not exist', '', '')
                gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_roi_by_user')
                return {'message': error.to_dict()}, 404

            roi_data = read_from_database_all_rows(db_query, (user_id,), database_config_file,
                                                   database_config_section_api, True)

            res_array = []

            for roi in roi_data:
                roi_obj = {
                    'roi_id': roi[0],
                    'roi_name': roi[1],
                    'description': roi[2],
                    'customer_id': roi[3],
                    'geoJSON': json.loads(roi[4]),
                    'creation_date': str(roi[5])
                }

                res_array.append(roi_obj)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            gemslog(LogLevel.WARNING, f"'message': {error.to_dict()}", 'API-get_roi_by_user')
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_roi_by_user')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-get_roi_by_user')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Successful response: {res_array}', 'API-get_roi_by_user')
            return {'rois': res_array}, 200
