########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# General token models for the Swagger UI
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import auth_namespace as api

########################################################################################################################
# Request model for the token expiration time
########################################################################################################################

exp_time_request_model = api.model('exp_time_request_model',
                                   {
                                       'bearer_token': fields.String(
                                           description='Bearer token for which the time should be set',
                                           example='ABCDEF1234'
                                       ),
                                       'exp_time': fields.Integer(
                                           description='Expiration duration in seconds',
                                           example=1000,
                                           min=1,
                                           max=2000000000
                                       ),
                                   })
