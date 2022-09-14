########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Service models for the Swagger UI
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
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
