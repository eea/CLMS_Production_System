########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# RabbitMQ list virtual hosts model for the Swagger UI
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

virtual_host_response_model = api.model('rabbitmq_virtual_hosts_response_model',
                                        {
                                            'virtual_hosts': fields.List(
                                                fields.String,
                                                description='List of all available RabbitMQ queues on this host',
                                                example=['virtual_host_1', 'virtual_host_2',
                                                         'virtual_host_3']
                                            )
                                        })

########################################################################################################################
# Request model for the DELETE request
########################################################################################################################

virtual_host_request_model = api.model('rabbitmq_queue_vhost_request_model',
                                   {
                                       'virtual_host': fields.String(
                                           description='RabbitMQ host address',
                                           example='/',
                                           required=True
                                       ),
                                       'queue_name': fields.String(
                                           description='RabbitMQ queue name',
                                           example='service_seasonality',
                                           required=True
                                       )
                                   })