########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Namespace creation for the API definitions
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask_restx import Namespace

########################################################################################################################
# Internal namespaces for the GeoVille stuff in the Swagger UI
########################################################################################################################

auth_namespace = Namespace('auth', description='Authentication related operations')
config_namespace = Namespace('config', description='Configuration related operations')
rabbitmq_namespace = Namespace('rabbitmq', description='RabbitMQ related operations')
crm_namespace = Namespace('crm', description='CRM related operations')
rois_namespace = Namespace('roi', description='Region of interest related operations')
service_namespace = Namespace('services', description='Service related operations')
logging_namespace = Namespace('logging', description='Logging related operations')
general_error_namespace = Namespace('error_models', description='Inlcudes all error models')
auth_header_namespace = Namespace('auth', description='Authentication header model')
