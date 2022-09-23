########################################################################################################################
#
# ServiceUnavailable error model
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import general_error_namespace as api
from models.models_error.error_base_model import error_definition
from werkzeug.exceptions import ServiceUnavailable

########################################################################################################################
# Nested response model for the ServiceUnavailable errors
########################################################################################################################

error_description = api.model('error_description_503_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=ServiceUnavailable.code,
        default=ServiceUnavailable.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='SERVICE_UNAVAILABLE',
        default='SERVICE_UNAVAILABLE'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=ServiceUnavailable.description,
        default=ServiceUnavailable.description
    )
})

error_dicts = api.model('error_dict_503_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition),
})

error_503_model = api.model('error_503_model', {
    'message': fields.Nested(error_dicts),
})
