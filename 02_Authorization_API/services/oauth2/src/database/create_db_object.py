########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Instantiation of the SQL Alchemy database object
#
# Date created: 08.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask_sqlalchemy import SQLAlchemy
from init.init_app import app

########################################################################################################################
# Initialising the SQL alchemy database connector
########################################################################################################################

db = SQLAlchemy(app)