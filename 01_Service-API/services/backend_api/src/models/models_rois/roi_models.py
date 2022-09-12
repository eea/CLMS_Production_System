########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Region of interest models for the Swagger UI
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
from init.namespace_constructor import rois_namespace as api

########################################################################################################################
# Request model for the POST request
########################################################################################################################

roi_id_model = api.model('roi_id_model',
                         {
                             'roi_id': fields.String(
                                 description='Region of interest identifier',
                                 example='aedadc0b181bca2166896cb737e99743de5a6df762e3c5d07b17b9dd6db86a1c',
                                 required=True
                             )
                         })

########################################################################################################################
# Model for the geoJSON representation
########################################################################################################################

geoJSON_model = api.model('geoJSON_model',
                          {
                              'type': fields.String(
                                  description='Type of geoJSON object',
                                  example='MultiPolygon',
                                  default='MultiPolygon',
                                  required=True
                              ),
                              'coordinates': fields.List(fields.List(fields.List(fields.List(fields.Float(
                                  description='One coordinate pair of XY',
                                  required=True
                              )))))
                          })

########################################################################################################################
# Request model for the ROI creation request
########################################################################################################################

roi_request_model = api.model('roi_request_model',
                              {
                                  'name': fields.String(
                                      description='A name to identify the ROI',
                                      example='957653b708d9715d631',
                                      required=True
                                  ),
                                  'description': fields.String(
                                      description='Descriptive text about the ROI',
                                      example='An example region of interest'
                                  ),
                                  'user_id': fields.String(
                                      description='Unique identifier of a customer',
                                      example='8KfYSDj8Wq2iNtIly98M5ES4',
                                      required=True
                                  ),
                                  'geoJSON': fields.Nested(
                                      geoJSON_model,
                                      description='GeoJSON representation of the ROI',
                                      example={"type": "MultiPolygon",
                                               "coordinates": [[[
                                                   [11.239013671875, 47.212105775622426],
                                                   [11.506805419921875, 47.212105775622426],
                                                   [11.506805419921875, 47.307171912070814],
                                                   [11.239013671875, 47.307171912070814],
                                                   [11.239013671875, 47.212105775622426]
                                               ]]]},
                                      required=True)
                              })

########################################################################################################################
# ROI response model for a single ROI
########################################################################################################################

single_roi_response_model = api.model('single_roi_response_model',
                                      {
                                          'name': fields.String(
                                              description='A name to identify the ROI',
                                              example='Region of Interest'
                                          ),
                                          'description': fields.String(
                                              description='Descriptive text about the ROI',
                                              example='An example region of interest'
                                          ),
                                          'user_id': fields.String(
                                              description='Unique identifier of a customer',
                                              example='8KfYSDj8Wq2iNtIly98M5ES4'
                                          ),
                                          'geoJSON': fields.Nested(
                                              geoJSON_model,
                                              description='GeoJSON representation of the ROI',
                                              example={"type": "MultiPolygon",
                                                       "coordinates": [[[
                                                           [11.239013671875, 47.212105775622426],
                                                           [11.506805419921875, 47.212105775622426],
                                                           [11.506805419921875, 47.307171912070814],
                                                           [11.239013671875, 47.307171912070814],
                                                           [11.239013671875, 47.212105775622426]
                                                       ]]]}
                                          ),
                                          'creation_date': fields.String(
                                              description='Date of creation of the ROI',
                                              example=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                                          ),
                                      })

########################################################################################################################
# ROI response model for several ROI's
########################################################################################################################

several_roi_response_model = api.model('roi_response_model',
                                       {
                                           'rois': fields.List(
                                               fields.Nested(
                                                   single_roi_response_model,
                                                   description="List of ROI's",
                                               )
                                           )
                                       })

########################################################################################################################
# Model for the ROI update request
########################################################################################################################

roi_attributes_request = api.model('roi_attributes_request',
                                   {
                                       'roi_id': fields.String(
                                           description='Unique identifier of a ROI',
                                           example='aedadc0b181bca2166896cb737e99743de5a6df762e3c5d07b17b9dd6db86a1c',
                                           required=True
                                       ),
                                       'name': fields.String(
                                           description='A name to identify the ROI',
                                           example='Name identifier of a Region of Interest'
                                       ),
                                       'description': fields.String(
                                           description='Descriptive ',
                                           example='An example region of interest'
                                       ),
                                       'user_id': fields.String(
                                           description='Unique identifier of a customer',
                                           example='8KfYSDj8Wq2iNtIly98M5ES4'
                                       ),
                                       'geoJSON': fields.Nested(
                                           geoJSON_model,
                                           description='GeoJSON of the region of interest',
                                           example={"type": "MultiPolygon",
                                                    "coordinates": [[[
                                                        [11.239013671875, 47.212105775622426],
                                                        [11.506805419921875, 47.212105775622426],
                                                        [11.506805419921875, 47.307171912070814],
                                                        [11.239013671875, 47.307171912070814],
                                                        [11.239013671875, 47.212105775622426]
                                                    ]]]}
                                       ),

                                   })

########################################################################################################################
# Model for the ROI update request
########################################################################################################################

roi_entity_request = api.model('roi_entity_request',
                               {
                                   'roi_id': fields.String(
                                       description='Unique identifier of a ROI',
                                       example='aedadc0b181bca2166896cb737e99743de5a6df762e3c5d07b17b9dd6db86a1c',
                                       required=True
                                   ),
                                   'name': fields.String(
                                       description='Name to identify the ROI',
                                       example='Name of a Region of Interest',
                                       required=True
                                   ),
                                   'description': fields.String(
                                       description='Descriptive ',
                                       example='Example region of interest'
                                   ),
                                   'user_id': fields.String(
                                       description='Unique identifier of a customer',
                                       example='8KfYSDj8Wq2iNtIly98M5ES4',
                                       required=True
                                   ),
                                   'geoJSON': fields.Nested(
                                       geoJSON_model,
                                       description='GeoJSON of the region of interest',
                                       example={"type": "MultiPolygon",
                                                "coordinates": [[[
                                                    [11.239013671875, 47.212105775622426],
                                                    [11.506805419921875, 47.212105775622426],
                                                    [11.506805419921875, 47.307171912070814],
                                                    [11.239013671875, 47.307171912070814],
                                                    [11.239013671875, 47.212105775622426]
                                                ]]]},
                                       required=True
                                   ),

                               })
