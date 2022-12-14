########################################################################################################################
#
# HTTP error 405 (Unsupported media type) error class definition
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.api_base_error.api_base_error import BaseError
from werkzeug.exceptions import TooManyRequests


########################################################################################################################
# UnsupportedMediaType error class
########################################################################################################################

class TooManyRequestsError(BaseError):
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
        self.code = TooManyRequests.code
        self.status = 'TOO_MANY_REQUESTS'
        self.description = TooManyRequests.description

        self.traceback = traceback
        self.payload = payload
        self.message = message
