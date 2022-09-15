########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# API call for creating a warning log message
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
from geoville_ms_logging.geoville_ms_logging import log, LogLevel
from init.init_env_variables import database_config_file, database_config_section_api
from init.namespace_constructor import logging_namespace as api
from lib.auth_header import auth_header_parser
from lib. database_helper import check_service_name_similarity
from models.models_error.http_error_401 import error_401_model
from models.models_error.http_error_403 import error_403_model
from models.models_error.http_error_500 import error_500_model
from models.models_error.http_error_503 import error_503_model
from models.models_logging.logging_models import logging_request_model
from oauth.oauth2 import require_oauth
import traceback


########################################################################################################################
# Resources definition for creating a warning log message via API call
########################################################################################################################

@api.header('Content-Type', 'application/json')
class LogWarning(Resource):
    """ Class for handling the POST request

    This class defines the API call for creating a warning log message. The class consists of one method which accepts a
    POST request. For the POST request two additional parameter are required.

    """

    ####################################################################################################################
    # Method for handling the POST request
    ####################################################################################################################

    @require_oauth(['admin', 'user'])
    @api.doc(body=logging_request_model, parser=auth_header_parser)
    @api.response(204, 'Operation was successful')
    @api.response(401, 'Unauthorized', error_401_model)
    @api.response(403, 'Forbidden', error_403_model)
    @api.response(500, 'Internal Server Error', error_500_model)
    @api.response(503, 'Service Unavailable', error_503_model)
    def post(self):
        """ POST definition for creating a warning log message

        <p style="text-align: justify">This method defines the handler for the POST request of the create warning log
        message script. It returns no message body and thus no contents. In contrast it returns the HTTP status code
        204.</p>

        <br><b>Description:</b>
        <p style="text-align: justify">This service route enables the possibility to write log messages into the central
        GEMS logging database without having implemented the corresponding Python module. Therefore the service can be
        called from several different programming languages via a simple curL command. The curL command can be retrieved
        by trying out the service.</p>

        <br><b>Request headers:</b>
        <ul>
        <li><p><i>Authorization: Bearer token in the format "Bearer XXXX"</i></p></li>
        </ul>

        <br><b>Request payload:</b>
        <ul>
        <li><p><i>module_name (str): name of the module which triggered log message</i></p></li>
        <li><p><i>log_message (str): actual log message</i></p></li>
        </ul>

        <br><b>Result:</b>
        <p style="text-align: justify">The result of the POST request does not contain any object or message in the
        response body. The HTTP status signalise the result of the submitted request. Any other response status code
        than 204, indicates an error during the execution.</p>

        """

        try:
            req_args = api.payload

            if not check_service_name_similarity(req_args['service_module_name'], database_config_file,
                                                 database_config_section_api):
                error = BadRequestError('Service name could not be found', api.payload, '')
                log('API-log_warning', LogLevel.ERROR, f"'message': {error.to_dict()}")
                return {'message': error.to_dict()}, 400

            log(req_args['service_module_name'], LogLevel.WARNING, req_args['log_message'])

        except AttributeError:
            error = ServiceUnavailableError('Could not connect to the database server', '', '')
            log('API-log_warning', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 503

        except Exception:
            error = InternalServerErrorAPI('Unexpected error occurred', api.payload, traceback.format_exc())
            log('API-log_warning', LogLevel.ERROR, f"'message': {error.to_dict()}")
            return {'message': error.to_dict()}, 500

        else:
            log('API-log_warning', LogLevel.INFO, f'Successfully stored log message')
            return '', 204
