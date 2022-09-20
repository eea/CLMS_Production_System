########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ list users model for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import rabbitmq_namespace as api

########################################################################################################################
# Response model for the POST and GET request
########################################################################################################################

users_object_model = api.model('rabbitmq_users_object',
                               {
                                   'name': fields.String(
                                       description='RabbitMQ user name',
                                       example='user_name'
                                   ),
                                   'permission': fields.String(
                                       description='Administration rights of the user',
                                       example='administrator'
                                   )
                               })

########################################################################################################################
# Response model for the GET request
########################################################################################################################

users_response_model = api.model('rabbitmq_users_response_model',
                                 {
                                     'users':fields.List(
                                         fields.Nested(
                                             users_object_model
                                         )
                                     )
                                 })
