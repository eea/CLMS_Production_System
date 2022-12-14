########################################################################################################################
#
# Queue configuration models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import config_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

add_queue_config_model = api.model('add_queue_config_model',
                                   {
                                       'service_id': fields.String(
                                           description='Unique identifier of a service',
                                           example='6237b6905d0d45',
                                           required=True
                                       ),
                                       'queue_name': fields.String(
                                           description='Name of the RabbitMQ queue',
                                           example='queue_name',
                                           required=True
                                       ),
                                       'host': fields.String(
                                           description='Host of the RabbitMQ instance',
                                           example='dev.services.geoville.com',
                                           required=True
                                       ),
                                       'port': fields.Integer(
                                           description='Port of the RabbitMQ instance',
                                           example=5672,
                                           required=True
                                       )
                                   })

########################################################################################################################
# Success model for the POST request
########################################################################################################################

queue_creation_success_model = api.model('queue_creation_success_model',
                                         {
                                             'service_id': fields.String(
                                                 description='Unique identifier of a service',
                                                 example='6237b6905d0d45',
                                                 required=True
                                             ),
                                             'queue_name': fields.String(
                                                 description='Name of the RabbitMQ queue',
                                                 example='queue_name',
                                                 required=True
                                             )
                                         })

########################################################################################################################
# Request model for the POST request
########################################################################################################################

delete_queue_config_model = api.model('delete_queue_config_model',
                                      {
                                          'queue': fields.String(
                                              description='Rabbit MQ queue name to be deleted',
                                              example='service_name',
                                              required=True
                                          )
                                      })

########################################################################################################################
# Response model for retrieving the entire configuration
########################################################################################################################

queue_config_list_model = api.model('queue_config_list_model',
                                    {
                                        'message_checker_config': fields.List(fields.Nested(
                                            add_queue_config_model,
                                            description='List of detailed message checker configurations')
                                        ),
                                    })
