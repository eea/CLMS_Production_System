########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Vector class attribution model for the Swagger UI
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
# Request model for the POST request
########################################################################################################################

vector_class_attribution_request_model = api.model('vector_class_attribution_request_model',
                                                   {
                                                       'vector': fields.String(
                                                           description='Vector path',
                                                           example='/vsis3/task22/tests/in/test1.shp',
                                                           required=True
                                                       ),
                                                       'raster': fields.String(
                                                           description='List of raster path',
                                                           example='/vsis3/task22/tests/in/test.tif',
                                                           required=True
                                                       ),
                                                       'subproduction_unit_name': fields.Integer(
                                                           description='Subproduction Unit Identifier',
                                                           example=123,
                                                           required=True
                                                       ),
                                                       'config': fields.String(
                                                           description='Config parameters for GDAL',
                                                           example="AWS_SECRET_ACCESS_KEY 123abc "
                                                                   "AWS_S3_ENDPOINT cf2.cloudferro.com:8080 "
                                                                   "AWS_VIRTUAL_HOSTING FALSE "
                                                                   "AWS_ACCESS_KEY_ID abc123",
                                                           required=True
                                                       ),
                                                       'method': fields.String(
                                                           description='Extraction Method',
                                                           example="relative_count",
                                                           required=True
                                                       ),
                                                       'method_params': fields.String(
                                                           description='Extraction Method',
                                                           example="1 7",
                                                           required=False
                                                       ),
                                                       'na_value': fields.Integer(
                                                           description='na value',
                                                           example=0,
                                                           required=False
                                                       ),
                                                       'col_names': fields.String(
                                                           description='List of column names',
                                                           example="occurrence_class_1 occurrence_class_7",
                                                           required=False
                                                       ),
                                                       'id_column': fields.String(
                                                           description='Column name of polygon id',
                                                           example="id",
                                                           required=True
                                                       ),
                                                       'bucket_path': fields.String(
                                                           description='Path to S3 bucket',
                                                           example="bucketname/folder/subfolder/",
                                                           required=True
                                                       ),
                                                       'reference_year': fields.Date(
                                                           description='Reference year to be requested',
                                                           example='2018',
                                                           required=True
                                                       ),
                                                       'user_id': fields.String(
                                                           description='ID of the current customer',
                                                           example='S6aIHB1NOSbaj1ghq99pXq9a',
                                                           required=True
                                                       ),
                                                       'service_name': fields.String(
                                                           description='Name of the service to be called',
                                                           example='vector_class_attribution',
                                                           pattern='(vector_class_attribution)',
                                                           required=True
                                                       )
                                                   })
