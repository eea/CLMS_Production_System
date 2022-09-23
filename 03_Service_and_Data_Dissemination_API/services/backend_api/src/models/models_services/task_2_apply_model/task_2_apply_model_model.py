########################################################################################################################
#
# Apply model for the Swagger UI
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
# Additional data filter model
########################################################################################################################

t2_apply_model_data_filter_model = api.model('t2_apply_model_data_filter_model',
                                             {
                                                 'min_time_difference': fields.Integer(
                                                     example=10,
                                                     required=False
                                                 ),
                                                 'max_cc_local': fields.Integer(
                                                     description='Start date to be requested',
                                                     minimum=0,
                                                     maximum=100,
                                                     default=0,
                                                     example=20,
                                                     required=False
                                                 )
                                             })

########################################################################################################################
# Request model for the POST request
########################################################################################################################

t2_apply_model_request_model = api.model('t2_apply_model_request_model',
                                         {
                                             'model_path': fields.String(
                                                 description='parameter for saving data',
                                                 example='path/to/my/model.pkl',
                                                 required=True
                                             ),
                                             'start_date': fields.Date(
                                                 description='Oldest acquisition date to consider',
                                                 example='2017-07-01',
                                                 default='2017-07-01',
                                                 required=True
                                             ),
                                             'end_date': fields.Date(
                                                 description='Newest acquisition date to consider',
                                                 example='2019-06-30',
                                                 default='2019-06-30',
                                                 required=True
                                             ),
                                             'processing_unit_name': fields.String(
                                                 description='Name of the processing unit',
                                                 example='10kmE0N70',
                                                 required=True
                                             ),
                                             'cloud_cover': fields.Integer(
                                                 description='Maximum cloud cover (in %) to consider',
                                                 example=80,
                                                 min=0,
                                                 max=100,
                                                 default=80,
                                                 required=True
                                             ),
                                             'interval_size': fields.Integer(
                                                 description='Time difference in days for temporal interpolation',
                                                 example=10,
                                                 default=10,
                                                 required=True
                                             ),
                                             's1_bands': fields.List(fields.String(
                                                 description='Names of the required Sentinel-1 bands or indices',
                                                 example='ASC_DVVVH',
                                                 required=False
                                             )),
                                             's2_bands': fields.List(fields.String(
                                                 description='Names of the required Sentinel-2 bands or indices',
                                                 example='B01',
                                                 required=False
                                             )),
                                             'precalculated_features': fields.List(fields.String(
                                                 description='Names of the required auxiliary features',
                                                 example='geomorpho90',
                                                 required=False
                                             )),
                                             'use_cache': fields.Boolean(
                                                 description='Use cache results',
                                                 example=True,
                                                 required=False
                                             ),
                                             'data_filter_s1': fields.Nested(
                                                 t2_apply_model_data_filter_model,
                                                 description='Use cache results',
                                                 required=False
                                             ),
                                             'data_filter_s2': fields.Nested(
                                                 t2_apply_model_data_filter_model,
                                                 description='Use cache results',
                                                 required=False
                                             ),
                                             'aoi_coverage': fields.Integer(
                                                 description='min coverage in percent for one scene of aoi',
                                                 example=20,
                                                 default=0,
                                                 minimum=0,
                                                 maximum=100,
                                                 required=False
                                             ),
                                             'user_id': fields.String(
                                                 description='ID of the current customer',
                                                 example='S6aIHB1NOSbaj1ghq99pXq9a',
                                                 required=True
                                             ),
                                             'service_name': fields.String(
                                                 description='Name of the service to be called',
                                                 example='task2_apply_model',
                                                 pattern='(task2_apply_model)',
                                                 required=True
                                             )
                                         })
