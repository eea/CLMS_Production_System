########################################################################################################################
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