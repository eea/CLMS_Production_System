########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Service success response models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Hypermedia service model
########################################################################################################################

hypermedia_model = api.model('hypermedia_model',
                             {
                                 'href': fields.String(
                                     description='URI to linked resource',
                                     example='/services/order_status/<order_id>'
                                 ),
                                 'rel': fields.String(
                                     description='Linked resource',
                                     example='services'
                                 ),
                                 'type': fields.String(
                                     description='Type of HTTP method',
                                     example='GET'
                                 )
                             })

########################################################################################################################
# Response model for the POST service request
########################################################################################################################

service_success_response_model = api.model('service_success_response_model',
                                           {
                                               'message': fields.String(
                                                   description='Success message',
                                                   example='Order successfully received'
                                               ),
                                               'links': fields.Nested(
                                                   hypermedia_model,
                                                   description='Hypermedia model'
                                               )
                                           })
