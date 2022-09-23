########################################################################################################################
#
# Task 1 reprocessing model for the Swagger UI
#
# Date created: 02.08.2021
# Date last modified: 02.08.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.08
#
########################################################################################################################

from datetime import date
from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Additional data filter model
########################################################################################################################

task_1_stitching_request_model = api.model('task_1_stitching_request_model',
                                           {
                                               'processing_unit_name': fields.String(
                                                   description='Input PU',
                                                   example='129_1',
                                                   required=True
                                               ),
                                               'surrounding_pus': fields.String(
                                                   description='List of surrounding PUs',
                                                   example='129_2, 174, 175',
                                                   required=True
                                               ),

                                               'user_id': fields.String(
                                                   description='ID of the current customer',
                                                   example='S6aIHB1NOSbaj1ghq99pXq9a',
                                                   required=True
                                               ),
                                               'service_name': fields.String(
                                                   description='Name of the service to be called',
                                                   example='task1_stitching',
                                                   pattern='(task1_stitching)',
                                                   required=True
                                               )
                                           })
