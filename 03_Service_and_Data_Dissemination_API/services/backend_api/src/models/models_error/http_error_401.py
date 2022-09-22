########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Unauthorized error model
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
from werkzeug.exceptions import Unauthorized

########################################################################################################################
# Nested response model for Unauthorized errors
########################################################################################################################

error_description = api.model('error_description_401_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=Unauthorized.code,
        default=Unauthorized.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='UNAUTHORIZED',
        default='UNAUTHORIZED'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=Unauthorized.description,
        default=Unauthorized.description
    )
})

error_dicts = api.model('error_dict_401_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition)
})

error_401_model = api.model('error_401_model', {
    'message': fields.Nested(error_dicts)
})
