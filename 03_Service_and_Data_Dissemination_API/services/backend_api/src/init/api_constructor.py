########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# API entry point
#
# Date created: 01.06.2020
# Date last modified: 07.07.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.07
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
                  version='21.08',
                  description='CLCplus Backbone Service API based on a Microservice architecture',
                  contact='IT-Services@geoville.com'
                  )
