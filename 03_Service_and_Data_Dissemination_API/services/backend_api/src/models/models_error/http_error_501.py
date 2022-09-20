########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# NotImplemented error model
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
from werkzeug.exceptions import NotImplemented

########################################################################################################################
# Nested response model for the NotImplemented errors
########################################################################################################################

error_description = api.model('error_description_501_model', {
    'code': fields.String(
        description='HTTP error status code',
        example=NotImplemented.code,
        default=NotImplemented.code
    ),
    'status': fields.String(
        description='HTTP error status',
        example='NOT_IMPLEMENTED',
        default='NOT_IMPLEMENTED'
    ),
    'description': fields.String(
        description='Detailed HTTP error description',
        example=NotImplemented.description,
        default=NotImplemented.description
    )
})

error_dicts = api.model('error_dict_501_model', {
    'error_description': fields.Nested(error_description),
    'error_definition': fields.Nested(error_definition),
})

error_501_model = api.model('error_501_model', {
    'message': fields.Nested(error_dicts),
})
