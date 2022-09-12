########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Error base definition model for all kind of errors
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from flask_restx import fields
from init.namespace_constructor import general_error_namespace as api

########################################################################################################################
# Error definition model for all kind of errors
########################################################################################################################

error_definition = api.model('error_definition_model', {
    'message': fields.String,
    'payload': fields.String(),
    'traceback': fields.String()
})
