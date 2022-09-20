########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Bearer token models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import auth_namespace as api

########################################################################################################################
# Request model for the POST request of the Bearer Token generation process
########################################################################################################################

bearer_token_request_model = api.model('get_bearer_token_request_model',
                                       {
                                           'user_id': fields.String(
                                               description='User specific client id',
                                               example='8KfYSDj8Wq2iNtIly98M5ES4',
                                               required=True
                                           ),
                                           'client_secret': fields.String(
                                               description='User specific client secret',
                                               example='Cgc8lMd5LozQz5ifiqMks',
                                               required=True
                                           )
                                       })

########################################################################################################################
# Response model for the POST request of the Bearer Token generation process
########################################################################################################################

bearer_token_response_model = api.model('bearer_token_response_model',
                                        {
                                            'access_token': fields.String(
                                                description='Bearer token for the user',
                                                example='ABCDEF1234'
                                            ),
                                            'expires_in': fields.Integer(
                                                description='The expiration duration',
                                                example=1000
                                            ),
                                            'refresh_token': fields.String(
                                                description='Refresh token for the user',
                                                example='ABCDEF1234'
                                            ),
                                            'token_type': fields.String(
                                                description='The type of the returned token',
                                                example='Bearer'
                                            )
                                        })
