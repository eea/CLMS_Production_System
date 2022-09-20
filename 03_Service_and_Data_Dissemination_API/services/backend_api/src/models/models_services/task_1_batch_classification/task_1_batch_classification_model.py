########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Task 1 batch classification model for the Swagger UI
#
# Date created: 15.04.2021
# Date last modified: 15.04.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.04
#
########################################################################################################################

from datetime import date
from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Additional data filter model
########################################################################################################################

t1_batch_classification_data_filter_model = api.model('t1_batch_classification_data_filter_model',
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

t1_batch_classification_request_model = api.model('t1_batch_classification_request_model',
                                                  {
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
                                                      'features': fields.List(fields.String(
                                                          description='Names of the required auxiliary features',
                                                          example='B01_MIN',
                                                          required=True
                                                      )),
                                                      'use_cache': fields.Boolean(
                                                          description='Use cache results',
                                                          example=True,
                                                          required=True
                                                      ),
                                                      'data_filter': fields.Nested(
                                                          t1_batch_classification_data_filter_model,
                                                          description='Data filter',
                                                          required=True
                                                      ),
                                                      'rule_set': fields.List(fields.String(
                                                          description='Apply rule set',
                                                          example="rule_1",
                                                          required=True
                                                      )),
                                                      'user_id': fields.String(
                                                          description='ID of the current customer',
                                                          example='S6aIHB1NOSbaj1ghq99pXq9a',
                                                          required=True
                                                      ),
                                                      'service_name': fields.String(
                                                          description='Name of the service to be called',
                                                          example='task1_batch_classification',
                                                          pattern='(task1_batch_classification)',
                                                          required=True
                                                      )
                                                  })
