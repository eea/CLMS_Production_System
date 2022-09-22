########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Service models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from datetime import datetime
from flask_restx import fields
from init.namespace_constructor import crm_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

service_creation_model = api.model('service_creation_model',
                                   {
                                       'service_name': fields.String(
                                           description='Unique name of a service',
                                           example='service_name',
                                           required=True
                                       ),
                                       'service_comment': fields.String(
                                           description='Description of what the service offers',
                                           example='The service calculates...'
                                       ),
                                       'service_validity': fields.Boolean(
                                           description='Indicator if the service is active',
                                           example=True,
                                           required=True
                                       ),
                                       'service_owner_geoville': fields.String(
                                           description='Responsible person within GeoVille',
                                           example='IT-Services',
                                           required=True
                                       ),
                                       'external': fields.Boolean(
                                           description='Internal or external service',
                                           example=True,
                                           required=True
                                       )
                                   })

########################################################################################################################
# Response model for the POST request
########################################################################################################################

service_id_model = api.model('service_id_model',
                             {
                                 'service_id': fields.String(
                                     description='Unique identifier of a service',
                                     example='69179d1f69e3766406e7008500a1fe468652c951055b419d254c070b9e59c001',
                                     required=True
                                 ),
                             })

########################################################################################################################
# Object model for the get_all_services GET request
########################################################################################################################

service_query_model = api.model('service_query_model',
                                 {
                                     'subproduction_unit': fields.String(
                                         description='Unique identifier of a sub-production unit',
                                         example='1_2'
                                     ),
                                     'processing_unit': fields.String(
                                         description='Unique identifier of a processing unit',
                                         example='10kmE108N256'
                                     ),
                                     'service_name': fields.String(
                                         description='Unique name of a service',
                                         example='service_name'
                                     ),
                                     'order_status': fields.String(
                                         description='Status of an order',
                                         example='order status'
                                     ),
                                     'order_id': fields.String(
                                         description='Unique identifier of an order',
                                         example='2bfedd049fb5cff841e4965fabbeec46'
                                     ),
                                     'order_json': fields.String(
                                         description='Order payload in form of a json',
                                         example='{"key": value}'
                                     ),
                                     'order_result': fields.String(
                                         description='Path to the order result',
                                         example='/.../result.tif'
                                     )
                                 })

service_object_model = api.model('service_object_model',
                                 {
                                     'service_id': fields.String(
                                         description='Unique identifier of a service',
                                         example='a798a06534046dadfac995b3f3806122317dba4391022a1f9296b911b789f344'
                                     ),
                                     'service_name': fields.String(
                                         description='Unique name of a service',
                                         example='service_name'
                                     ),
                                     'service_comment': fields.String(
                                         description='Description of what the service offers',
                                         example='The service calculates...'
                                     ),
                                     'service_validity': fields.Boolean(
                                         description='Indicator if the service is active',
                                         example=True
                                     ),
                                     'service_owner_geoville': fields.String(
                                         description='Responsible person within GeoVille',
                                         example='IT-Services'
                                     ),
                                     'external': fields.Boolean(
                                         description='Internal or external service',
                                         example=True
                                     ),
                                     'date_of_creation': fields.DateTime(
                                         description='Date of creation of the service',
                                         example=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                                     )
                                 })

########################################################################################################################
# Response model for the get_all_services GET request
########################################################################################################################

service_list_model = api.model('service_list_model',
                               {
                                   'services': fields.List(fields.Nested(
                                       service_object_model,
                                       description='Detailed service information')
                                   ),
                               })

query_list_model = api.model('query_list_model',
                               {
                                   'services': fields.List(fields.Nested(
                                       service_query_model,
                                       description='Detailed query information')
                                   ),
                               })