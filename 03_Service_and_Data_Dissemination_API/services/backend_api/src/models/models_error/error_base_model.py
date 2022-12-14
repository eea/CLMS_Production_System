########################################################################################################################
#
# Error base definition model for all kind of errors
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
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
