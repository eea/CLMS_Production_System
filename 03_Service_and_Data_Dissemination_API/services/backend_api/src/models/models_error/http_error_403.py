########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Forbidden error model
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
from werkzeug.exceptions import Forbidden

########################################################################################################################
# Nested response model for Forbidden errors
########################################################################################################################

error_description = api.model('error_description_403_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=Forbidden.code,
        default=Forbidden.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='FORBIDDEN',
        default='FORBIDDEN'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=Forbidden.description,
        default=Forbidden.description
    )
})

error_dicts = api.model('error_dict_403_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition)
})

error_403_model = api.model('error_403_model', {
    'message': fields.Nested(error_dicts)
})
