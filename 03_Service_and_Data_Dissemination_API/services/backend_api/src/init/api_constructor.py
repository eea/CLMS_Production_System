########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# API entry point
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask import Blueprint
from flask_restx import Api

########################################################################################################################
# Definition of the Swagger UI for the internal GeoVille API
########################################################################################################################

clcplus_blueprint = Blueprint('clcplus_api', __name__, url_prefix='/v1')

clcplus_api = Api(clcplus_blueprint,
                  title='CLCplus Backbone API',
                  version='20.06',
                  description='CLCplus Backbone Service API based on a Microservice architecture <style>.models {display: none !important}</style>',
                  contact='IT-Services@geoville.com'
                  )
