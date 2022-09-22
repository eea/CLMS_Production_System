########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Configuration file for the gunicorn server
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

pidfile = 'geoville_rest_api.pid'
proc_name = 'geoville_rest_api'
workers = 3
bind = '0.0.0.0:8080'
backlog = 2048
accesslog = '-'
errorlog = '-'
timeout = 1200
keepalive = 2
