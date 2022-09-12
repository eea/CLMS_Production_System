########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ server status model for the Swagger UI
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import rabbitmq_namespace as api

########################################################################################################################
# Response model for the POST and GET request
########################################################################################################################

rabbitmq_response_model = api.model('rabbitmq_server_status_response_model',
                                    {
                                        'host': fields.String(
                                            description='RabbitMQ host address',
                                            example='0.0.0.0'
                                        ),
                                        'server_status': fields.String(
                                            description='The server status',
                                            example='up and running'
                                        )
                                    })
