########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# WSGI entry point for gunicorn
#
# Date created: 19.09.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10
#
########################################################################################################################

from app import app

########################################################################################################################
# Starts the FLASK app
########################################################################################################################

if __name__ == "__main__":

    app.run()
