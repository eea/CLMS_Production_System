########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# HTTP error 501 (Not Implemented) error class definition
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################

from error_classes.api_base_error.api_base_error import BaseError
from werkzeug.exceptions import NotImplemented


########################################################################################################################
# NotImplemented error class
########################################################################################################################

class NotImplementedError(BaseError):
    """ Class definition

    This method is the is constructor method for

    """

    def __init__(self, message, payload, traceback):
        """ Constructor method

        This method is the is constructor method for

        Arguments:

            payload (str): Payload of the current request
            message (str): Individual message derived from the resource
            traceback (str): Error traceback

        """

        BaseError.__init__(self)
        self.code = NotImplemented.code
        self.status = 'NOT_IMPLEMENTED'
        self.description = NotImplemented.description

        self.traceback = traceback
        self.payload = payload
        self.message = message
