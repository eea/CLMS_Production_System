########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Harmonics model for the Swagger UI
#
# Date created: 01.06.2020
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

harmonics_request_model = api.model('harmonics_request_model',
                                    {
                                        'tile_id': fields.String(
                                            description='Sentinel-2 tile ID',
                                            example='33UXP',
                                            required=True
                                        ),
                                        'start_date': fields.Date(
                                            description='Start date to be requested',
                                            example=date.today().strftime('%Y-%m-%d'),
                                            required=True
                                        ),
                                        'end_date': fields.Date(
                                            description='End date to be requested',
                                            example=date.today().strftime('%Y-%m-%d'),
                                            required=True
                                        ),
                                        'band': fields.String(
                                            description='Processing level parameter',
                                            example='RED',
                                            required=True
                                        ),
                                        'resolution': fields.Integer(
                                            description='Resolution in meters',
                                            example=10,
                                            required=True
                                        ),
                                        'ndi_band': fields.String(
                                            description='Processing level parameter',
                                            example="None",
                                            required=True
                                        ),
                                        'user_id': fields.String(
                                            description='ID of the current customer',
                                            example='S6aIHB1NOSbaj1ghq99pXq9a',
                                            required=True
                                        ),
                                        'service_name': fields.String(
                                            description='Name of the service to be called',
                                            example='harmonics',
                                            pattern='(harmonics)',
                                            required=True
                                        )
                                    })
