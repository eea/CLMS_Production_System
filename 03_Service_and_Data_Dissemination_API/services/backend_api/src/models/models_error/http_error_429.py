########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# UnsupportedMediaType error model
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
from werkzeug.exceptions import TooManyRequests

########################################################################################################################
# Nested response model for the UnsupportedMediaType errors
########################################################################################################################

error_description = api.model('error_description_429_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=TooManyRequests.code,
        default=TooManyRequests.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='TOO_MANY_REQUESTS',
        default='TOO_MANY_REQUESTS'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=TooManyRequests.description,
        default=TooManyRequests.description
    )
})

error_dicts = api.model('error_dict_429_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition),
})

error_429_model = api.model('error_429_model', {
    'message': fields.Nested(error_dicts),
})
