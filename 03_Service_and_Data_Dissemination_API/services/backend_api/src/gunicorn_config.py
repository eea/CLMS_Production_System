########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Configuration file for the gunicorn server
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
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
