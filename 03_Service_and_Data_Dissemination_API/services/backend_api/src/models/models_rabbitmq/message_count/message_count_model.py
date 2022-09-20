########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ message count model for the Swagger UI
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
# Response model for the POST request
########################################################################################################################

message_count_model = api.model('rabbitmq_message_count_response_model',
                                {
                                    'virtual_host': fields.String(
                                        description='RabbitMQ virtual host address',
                                        example='/'
                                    ),
                                    'queue_name': fields.String(
                                        description='RabbitMQ queue name',
                                        example='queue_name'
                                    ),
                                    'message_count': fields.Integer(
                                        description='Number of messages in the specified queue',
                                        example=5
                                    )
                                })
