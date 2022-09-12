########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Index Page for the API Gateway
#
# Date created: 28.09.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.2
#
########################################################################################################################

from database.create_db_object import db

########################################################################################################################
# Adding the models to be created at start-up
########################################################################################################################

from models.model_oauth_client import OAuth2Client
from models.model_oauth_token import OAuth2Token
from models.model_user import User

try:
    db.create_all()

except:
    print("OAuth2 tables were already generated")