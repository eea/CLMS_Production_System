########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Models for the logger service
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import logging_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

logging_request_model = api.model('logging_request_model',
                                  {
                                      'service_module_name': fields.String(
                                          description='Name of the service and module which triggers the logger call',
                                          example='service_module',
                                          required=True
                                      ),
                                      'log_message': fields.String(
                                          description='Detailed log description',
                                          example='This is a log message',
                                          required=True
                                      )
                                  })
