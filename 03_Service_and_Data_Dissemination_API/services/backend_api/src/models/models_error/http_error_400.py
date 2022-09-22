########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# BadRequest error model
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
from werkzeug.exceptions import BadRequest

########################################################################################################################
# Nested response model for a BadRequest error
########################################################################################################################

error_description = api.model('error_description_400_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=BadRequest.code,
        default=BadRequest.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='BAD_REQUEST',
        default='BAD_REQUEST'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=BadRequest.description,
        default=BadRequest.description
    )
})

error_dicts = api.model('error_dict_400_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition)
})

error_400_model = api.model('error_400_model', {
    'message': fields.Nested(error_dicts)
})
