########################################################################################################################
#
# Service success response models for the Swagger UI
#
# Date created: 01.06.2020
# Date last modified: 15.04.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.04
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Hypermedia service model
########################################################################################################################

parameter_model = api.model('parameter_model',
                            {

                            })

########################################################################################################################
# Response model for the POST service request
########################################################################################################################

batch_classification_model = api.model('batch_classification_model',
                                       {
                                           'params': fields.Nested(
                                               parameter_model,
                                               required=True
                                           ),
                                           'service_name': fields.String(
                                               description='Name of the service to be called',
                                               example='batch_classification_test',
                                               pattern='(batch_classification_test)',
                                               required=True
                                           )
                                       })

########################################################################################################################
# Response model for the POST request
########################################################################################################################

batch_classification_production_model = api.model('batch_classification_production_model',
                                       {
                                           'params': fields.Nested(
                                               parameter_model,
                                               required=True
                                           ),
                                           'service_name': fields.String(
                                               description='Name of the service to be called',
                                               example='batch_classification_production',
                                               pattern='(batch_classification_production)',
                                               required=True
                                           )
                                       })

########################################################################################################################
# Response model for the POST request of the staging request
########################################################################################################################

batch_classification_staging_model = api.model('batch_classification_staging_model',
                                       {
                                           'params': fields.Nested(
                                               parameter_model,
                                               required=True
                                           ),
                                           'service_name': fields.String(
                                               description='Name of the service to be called',
                                               example='batch_classification_staging',
                                               pattern='(batch_classification_staging)',
                                               required=True
                                           )
                                       })
