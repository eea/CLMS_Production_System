########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Client models for the Swagger UI
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
# Request model for the POST request of the OAuth2 client creation
########################################################################################################################

auth_client_request_model = api.model('auth_client_request_model',
                                      {
                                          'client_name': fields.String(
                                              description='Name of the new customer',
                                              example='Max Mustermann',
                                              required=True
                                          )
                                      })

########################################################################################################################
# Response model for the POST request of the OAuth2 client creation
########################################################################################################################

auth_client_response_model = api.model('auth_client_response_model',
                                       {
                                           'user_id': fields.String(
                                               description='Client ID returned from the endpoint',
                                               example='8KfYSDj8Wq2iNtIly98M5ES4'
                                           ),
                                           'user_id': fields.String(
                                               description='Client secret returned from the endpoint',
                                               example='Cgc8lMd5LozQz5ifiqMks'
                                           )
                                       })

########################################################################################################################
# Client response model
########################################################################################################################

client_response_model = api.model('client_response_model',
                                   {
                                       'user_id': fields.String(
                                           description='User specific client ID',
                                           example='8KfYSDj8Wq2iNtIly98M5ES4'
                                       ),
                                       'client_name': fields.String(
                                           description='Complete name of the client',
                                           example='Max Mustermann'
                                       ),
                                       'grant_type': fields.String(
                                           description='User specific grant type of the OAuth flow',
                                           example='password'
                                       ),
                                       'response_type': fields.String(
                                           description='User specific response type of the OAuth flow',
                                           example='code'
                                       ),
                                       'scope': fields.String(
                                           description='Authorization scope for the user',
                                           example='user'
                                       )
                                   })

########################################################################################################################
# List of clients response model
########################################################################################################################

clients_list_response_model = api.model('clients_list_response_model',
                                        {
                                            'oauth_clients': fields.List(
                                                fields.Nested(client_response_model)
                                            ),
                                        })
