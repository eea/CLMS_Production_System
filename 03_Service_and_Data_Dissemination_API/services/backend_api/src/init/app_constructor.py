########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Flask App entry point
#
# Date created: 01.06.2020
# Date last modified: 01.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from blueprints.hello_Geoville.hello_geoville import index_page
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os

########################################################################################################################
# Template folder retrieval
########################################################################################################################

template_dir = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], 'templates')

########################################################################################################################
# Creation of the Flask App entry point
########################################################################################################################

app = Flask(__name__)

########################################################################################################################
# Configuration of the Flask App depending on ENV variable
########################################################################################################################

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")

else:
    app.config.from_object("config.DevelopmentConfig")

########################################################################################################################
# Creation of the Limiter object for limiting access to particular routes
########################################################################################################################

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

########################################################################################################################
# Added CORS for the app
########################################################################################################################

CORS(app)

########################################################################################################################
# Password encryption for the resource owner user creation
########################################################################################################################

bcrypt = Bcrypt(app)

########################################################################################################################
# Register the blueprints
########################################################################################################################

app.register_blueprint(index_page)
