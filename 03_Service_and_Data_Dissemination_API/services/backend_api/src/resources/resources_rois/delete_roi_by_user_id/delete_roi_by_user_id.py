########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Delete region of interest by ID API call
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from error_classes.http_error_503.http_error_503 import ServiceUnavailableError
from flask_restx import Resource
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import gemslog, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import rois_namespace as api
from lib.auth_header import auth_header_parser
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the delete region of interest by ID API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('user_id', 'User ID to be deleted')
class DeleteROIByUserID(Resource):
    """ Class for handling the DELETE request

    This class defines the API call for the delete region of interest by ID script. The class consists of one method
    which accepts a DELETE request. For the DELETE request a JSON with one parameter is required and defined in the
    corresponding model.

    """

    ####################################################################################################################
    # Method for handling the DELETE request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.expect(auth_header_parser)
    @api.response(204, 'Operation successful')
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def delete(self, user_id):
        """ DELETE definition for removing a region of interest by a customer ID

        <p style="text-align: justify">This method defines the handler for the DELETE request of the delete region of
        interests by customer ID script. It returns no message body and thus no contents. In contrast it returns the
        HTTP status code 204.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This GEMS service can be used by a GEMS API consumer in order to delete all
        stored region of interests belonging to GEMS customer by specifying the corresponding customer ID. As common use
        in API design, all DELETE request will not provide any return message from service. Only the HTTP status code
        should be checked for retrieving the result of the request.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Path parameters:</b>
        <ul>
        <li><p><i>customer_id (str): Unique identifier for a GEMS customer</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the DELETE request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicated an error during the execution.</p>

        """

        try:
            db_query = "UPDATE customer.region_of_interests SET deleted_at = NOW() WHERE roi_id = %s"
            execute_database(db_query, (user_id,), database_config_file, database_config_section_api, True)

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-delete_roi_by_user')
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            gemslog(LogLevel.ERROR, f"'message': {error.to_dict()}", 'API-delete_roi_by_user')
            return {'message': error.to_dict()}, 500

        else:
            gemslog(LogLevel.INFO, f'Deleted ROI with user ID {user_id}', 'API-delete_roi_by_user')
            return '', 204
