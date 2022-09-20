########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Get Products model for the Swagger UI
#
# Date created: 23.07.2021
# Date last modified: 23.07.2021
#
# __author__  = Johannes Schmid (schmid@geoville.com)
# __version__ = 21.07
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import service_namespace as api

########################################################################################################################
# Request model for the POST request get_product
########################################################################################################################

products_request_model = api.model('products_request_model',
                                    {
                                        'product': fields.String(
                                            description='Name of the CLC+ Backbone product',
                                            example='Raster',
                                            required=True
                                        ),
                                        'aoi': fields.String(
                                            description='Area of Interest as MultiPolygon (WKT) in WGS84 (EPSG:4326)',
                                            example='MULTIPOLYGON (((17.227309445590443 46.668932137424534, 17.2371487027879 47.10769387054001, 18.217384701084143 47.095973145761874, 18.19278655809051 46.65458260506014, 17.227309445590443 46.668932137424534)))',
                                            required=True
                                        ),
                                        'user_id': fields.String(
                                            description='ID of the current customer',
                                            example='S6aIHB1NOSbaj1ghq99pXq9a',
                                            required=True
                                        )
                                    })


########################################################################################################################
# Request model for the POST request get_national_product
########################################################################################################################

national_products_request_model = api.model('national_products_request_model',
                                    {
                                        'product': fields.String(
                                            description='Name of the CLC+ Backbone product',
                                            example='Raster',
                                            required=True
                                        ),
                                        'nation': fields.String(
                                            description='Country name in English (e.g. Austria)',
                                            example='Austria',
                                            required=True
                                        ),
                                        'user_id': fields.String(
                                            description='ID of the current customer',
                                            example='S6aIHB1NOSbaj1ghq99pXq9a',
                                            required=True
                                        )
                                    })


########################################################################################################################
# Request model for the POST request get_product_europe
########################################################################################################################

european_products_request_model = api.model('european_products_request_model',
                                    {
                                        'product': fields.String(
                                            description='Name of the CLC+ Backbone product',
                                            example='Raster',
                                            required=True
                                        ),
                                        'user_id': fields.String(
                                            description='ID of the current customer',
                                            example='S6aIHB1NOSbaj1ghq99pXq9a',
                                            required=True
                                        )
                                    })


########################################################################################################################
# Request model for the POST request get_national_product
########################################################################################################################

nations_request_model = api.model('nations_request_model',
                                    {
                                        'user_id': fields.String(
                                            description='ID of the current customer',
                                            example='S6aIHB1NOSbaj1ghq99pXq9a',
                                            required=True
                                        )
                                    })

########################################################################################################################
# Response model for getting national and europe products
########################################################################################################################

products_success_response_model = api.model('products_success_response_model',
                                           {
                                               'result': fields.String(
                                                   description='Download Link of the requested product',
                                                   example='https://s3.waw2-1.cloudferro.com/swift/v1/AUTH_abc/'
                                                           'clcplus-public/products/'
                                                           'CLMS_CLCplus_RASTER_2018_010m_eu_03035_V1_1.tif'
                                               )
                                           })

########################################################################################################################
# Response model for getting the nations
########################################################################################################################

nations_success_response_model = api.model('nations_success_response_model',
                                           {
                                               'nations': fields.List(
                                                   fields.String,
                                                   description='List of nation names that can be used as input for g'
                                                               'et_national_product',
                                                   example=["Austria", "Germany", "etc."]
                                               )
                                           })