########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Retransformation model for the Swagger UI
#
# Date created: 07.07.2021
# Date last modified: 07.07.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.07
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Retransformation request model
########################################################################################################################

retransformation_request_model = api.model('retransformation_request_model',
                                           {
                                               'subproduction_unit_name ': fields.String(
                                                   example='1_1',
                                                   required=True
                                               ),
                                               'user_id': fields.String(
                                                   description='ID of the current user',
                                                   example='S6aIHB1NOSbaj1ghq99pXq9a',
                                                   required=True
                                               ),
                                               'service_name': fields.String(
                                                   description='Name of the service to be called',
                                                   example='retransformation',
                                                   pattern='(retransformation)',
                                                   required=True
                                               )
                                           })
