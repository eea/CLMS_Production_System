########################################################################################################################
#
# HTTP error 422(Unsupported media type) error class definition
#
# Date created: 23.02.2021
# Date last modified: 23.02.2021
#
# __author__  = Patrick Wolf (wolf@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from error_classes.api_base_error.api_base_error import BaseError
from werkzeug.exceptions import UnprocessableEntity


########################################################################################################################
# UnsupportedMediaType error class
########################################################################################################################

class UnprocessableEntityError(BaseError):
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
        self.code = UnprocessableEntity.code
        self.status = 'UNPROCESSABLE_ENTITY'
        self.description = UnprocessableEntity.description

        self.traceback = traceback
        self.payload = payload
        self.message = message
