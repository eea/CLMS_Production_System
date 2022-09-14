########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Initialisation script for the environment variables
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Florian Girtler (girtler@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

import os

########################################################################################################################
# Database environment variables
########################################################################################################################

db_ini_file = os.environ.get("DATABASE_CONFIG_FILE")
db_ini_section = os.environ.get("DATABASE_CONFIG_FILE_SECTION")

########################################################################################################################
# Mail server environment variables
########################################################################################################################

mail_host = os.environ.get("MAIL_SERVER")
mail_port = os.environ.get("MAIL_PORT")
mail_user = os.environ.get("MAIL_USERNAME")
mail_pass = os.environ.get("MAIL_PASSWORD")

########################################################################################################################
# Mail server environment variables
########################################################################################################################

queue_service_name = os.environ.get('QUEUE_SERVICE_NAME')