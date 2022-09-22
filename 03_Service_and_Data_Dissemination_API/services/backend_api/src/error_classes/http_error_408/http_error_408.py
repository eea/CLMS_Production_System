########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# HTTP error 408 (Request Timeout) error class definition
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.api_base_error.api_base_error import BaseError
from werkzeug.exceptions import RequestTimeout


########################################################################################################################
# Request Timeout error class
########################################################################################################################

class RequestTimeoutError(BaseError):
    """ Class definition

    This class defines the error handler for a request timeout error.

    """

    def __init__(self, message, payload, traceback):
        """ Constructor method

        This method is the is constructor method for the request timeout error

        Arguments:
            payload (str): Payload of the current request
            message (str): Individual message derived from the resource
            traceback (str): Error traceback

        """

        BaseError.__init__(self)
        self.code = RequestTimeout.code
        self.status = 'REQUEST_TIMEOUT'
        self.description = RequestTimeout.description

        self.traceback = traceback
        self.payload = payload
        self.message = message
