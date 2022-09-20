########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Bearer token models for the Swagger UI
#
# Date created: 02.03.2020
# Date last modified: 01.07.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.07
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import auth_namespace as api

########################################################################################################################
# Request model for the POST request of the Bearer Token generation process
########################################################################################################################

login_request_model = api.model('login_request_model',
                                {
                                    'email': fields.String(
                                        description='E-mail address of the user',
                                        example='max@mustermann.de',
                                        required=True
                                    ),
                                    'password': fields.String(
                                        description='Password of the user login',
                                        example='Cgc8lMd5LozQz5ifiqMks',
                                        required=True
                                    )
                                })

########################################################################################################################
# Response model for the POST request of the Bearer Token generation process
########################################################################################################################

login_response_model = api.model('login_response_model',
                                 {
                                     'access_token': fields.String(
                                         description='Bearer token for the user',
                                         example='ABCDEF1234'
                                     ),
                                     'expires_in': fields.Integer(
                                         description='The expiration duration in seconds',
                                         example=1000
                                     ),
                                     'refresh_token': fields.String(
                                         description='Refresh token for the user',
                                         example='ABCDEF1234'
                                     ),
                                     'token_type': fields.String(
                                         description='The type of the returned token',
                                         example='Bearer'
                                     ),
                                     'client_id': fields.String(
                                         description='Client ID returned from the endpoint',
                                         example='8KfYSDj8Wq2iNtIly98M5ES4'
                                     ),
                                     'client_secret': fields.String(
                                         description='Client secret returned from the endpoint',
                                         example='Cgc8lMd5LozQz5ifiqMks'
                                     )
                                 })
