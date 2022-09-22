########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Index Page for the API Gateway
#
# Date created: 19.09.2019
# Date last modified: 21.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Flask
from flask_bcrypt import Bcrypt
import os

########################################################################################################################
# Initialising the Flask app
########################################################################################################################

app = Flask(__name__, template_folder='../templates')

########################################################################################################################
# Loading of the correct config file depending
########################################################################################################################

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")

else:
    app.config.from_object("config.DevelopmentConfig")

########################################################################################################################
# Needs to be set in case self-signed SSL ca_certificates are available
########################################################################################################################

os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

########################################################################################################################
# Password encryption for the resource owner user creation
########################################################################################################################

bcrypt = Bcrypt(app)