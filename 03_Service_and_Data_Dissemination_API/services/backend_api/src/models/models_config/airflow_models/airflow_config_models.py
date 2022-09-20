########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Airflow config models for the Swagger UI
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
# Request model for the POST request of adding a new Airflow entry
########################################################################################################################

add_airflow_config_model = api.model('add_airflow_config_model',
                                     {
                                         'service_name': fields.String(
                                             description='Unique identifier of a service',
                                             example='service_name',
                                             required=True
                                         ),
                                         'command': fields.String(
                                             description='Command to trigger the DAG',
                                             example='airflow trigger_dag',
                                             required=True
                                         ),
                                         'description': fields.String(
                                             description='Short description of the service and command',
                                             example='The command triggers the DAG for the service',
                                             required=True
                                         ),
                                     })

########################################################################################################################
# Request model for the POST request of deleting an Airflow entry by service name
########################################################################################################################

airflow_config_success_model = api.model('airflow_config_success_model',
                                          {
                                              'service_name': fields.String(
                                                  description='Name of the service',
                                                  example='service_name',
                                                  required=True
                                              )
                                          })

########################################################################################################################
# Response model for retrieving the entire configuration
########################################################################################################################

airflow_config_list_model = api.model('airflow_config_list_model',
                                      {
                                          'airflow_config': fields.List(fields.Nested(
                                              add_airflow_config_model,
                                              description='List of detailed airflow configurations')
                                          ),
                                      })
