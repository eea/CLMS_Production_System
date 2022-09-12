########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Delete an OAuth2 client by ID API call
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
from geoville_ms_database.geoville_ms_database import execute_database
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_oauth
from init.namespace_constructor import auth_namespace as api
from lib.auth_header import auth_header_parser
from models.models_error.http_error_400 import error_400_model
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resource definition for the OAuth2 client by ID API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
@api.param('client_id', 'Client to be deleted')
class DeleteOAuthClient(Resource):
    """ Class for handling the DELETE request

    This class defines the API call for the delete OAuth2 client by ID script. The class consists of one method which
    accepts a DELETE request. For the DELETE request an additional path parameter is required.

    """

    ####################################################################################################################
    # Method for handling the DELETE request
    ####################################################################################################################

    @require_oauth(['admin'])
    @api.doc(parser=auth_header_parser)
    @api.response(204, 'Operation successful')
    @api.response(400, 'Validation Error', error_400_model)
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def delete(self, client_id):
        """ DELETE definition for removing an OAuth2 client by ID

        <p style="text-align: justify">This method defines the handler for the DELETE request of the delete OAuth2
        client by ID script. It returns no message body and thus no contents. In contrast it returns the HTTP status
        code 204.</p>

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
        <p style="text-align: justify">The result of the DELETE request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicates an error during the execution.</p>

        """

        try:
            log('API-delete_client_id', LogLevel.INFO, f'Request path parameter: {client_id}')

            db_query = "DELETE FROM public.oauth2_client WHERE client_id = %s"
            execute_database(db_query, (client_id,), database_config_file, database_config_section_oauth, True)

        except KeyError as err:
            error = BadRequestError(f'Key error resulted in a BadRequest: {err}', api.payload, traceback.format_exc())
            log('API-delete_client_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 400

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-delete_client_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', '', traceback.format_exc())
            log('API-delete_client_id', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-delete_client_id', LogLevel.INFO, f'Successfully removed OAuth client with ID: {client_id}')
            return '', 204
