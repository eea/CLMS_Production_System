########################################################################################################################
#
# Unauthorized model for the API call
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
from werkzeug.exceptions import MethodNotAllowed

########################################################################################################################
# Nested response model for the MethodNotAllowed errors
########################################################################################################################

error_description = api.model('error_description_405_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=MethodNotAllowed.code,
        default=MethodNotAllowed.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='METHOD_NOT_ALLOWED',
        default='METHOD_NOT_ALLOWED'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=MethodNotAllowed.description,
        default=MethodNotAllowed.description
    )
})

error_dicts = api.model('error_dict_405_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition),
})

error_405_model = api.model('error_405_model', {
    'message': fields.Nested(error_dicts),
})
