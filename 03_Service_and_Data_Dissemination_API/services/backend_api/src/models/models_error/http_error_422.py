########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# NotFound error model
#
# Date created: 23.02.2021
# Date last modified: v
#
# __author__  = Patrick wolf (wolf@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import general_error_namespace as api
from models.models_error.error_base_model import error_definition
from werkzeug.exceptions import UnprocessableEntity

########################################################################################################################
# Nested response model for a UnprocessableEntity error
########################################################################################################################

error_description = api.model('error_description_422_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=UnprocessableEntity.code,
        default=UnprocessableEntity.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='UNPROCESSABLE_ENTITY',
        default='UNPROCESSABLE_ENTITY'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=UnprocessableEntity.description,
        default=UnprocessableEntity.description
    )
})

error_dicts = api.model('error_dict_422_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition)
})

error_422_model = api.model('error_422_model', {
    'message': fields.Nested(error_dicts)
})
