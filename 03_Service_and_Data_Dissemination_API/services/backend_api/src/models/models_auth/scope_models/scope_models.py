########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Scope models for the Swagger UI
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
# Request model for the PUT request
########################################################################################################################

scope_update_request_model = api.model('scope_update_request_model',
                                       {
                                           'client_id': fields.String(
                                               description='User specific client ID',
                                               example='8KfYSDj8Wq2iNtIly98M5ES4',
                                               required=True
                                           ),
                                           'scope': fields.String(
                                               description='Authorization scope for the user',
                                               example='user',
                                               required=True
                                           )
                                       })

########################################################################################################################
# Response model for the POST request
########################################################################################################################

scope_response_model = api.model('scope_response_model',
                                 {
                                     'client_id': fields.String(
                                         description='User specific client ID',
                                         example='8KfYSDj8Wq2iNtIly98M5ES4'
                                     ),
                                     'scope': fields.String(
                                         description='Authorization scope for the user',
                                         example='user'
                                     )
                                 })

########################################################################################################################
# Response model for the GET request
########################################################################################################################

scope_list_response_model = api.model('scope_list_response_model',
                                      {
                                          'scopes': fields.List(
                                              fields.Nested(scope_response_model)
                                          ),
                                      })