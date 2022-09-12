########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Service order status model for the Swagger UI
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Response model for the order status POST request
########################################################################################################################

order_status_response_model = api.model('order_status_response_model',
                                        {
                                            'order_id': fields.String(
                                                description='ID of the created order',
                                                example='391d3b45f059f9fb74b79868f6e8511e'
                                            ),
                                            'status': fields.String(
                                                description='Status message',
                                                example='SUCCESS'
                                            ),
                                            'result': fields.String(
                                                description='Link to the result file',
                                                example='https://gems-demo.s3.amazonaws.com'
                                            )
                                        })
