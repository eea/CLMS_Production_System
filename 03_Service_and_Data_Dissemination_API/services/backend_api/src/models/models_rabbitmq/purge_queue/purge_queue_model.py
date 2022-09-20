########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# RabbitMQ purge queue model for the API call
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
# Response model for the DELETE request
########################################################################################################################

purge_queue_response = api.model('rabbitmq_purge_queue_response_model',
                                 {
                                     'success': fields.String(
                                         description='Success message',
                                         example='Queue deleted'
                                     )
                                 })
