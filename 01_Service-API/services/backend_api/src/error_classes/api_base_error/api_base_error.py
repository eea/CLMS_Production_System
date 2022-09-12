########################################################################################################################
#
# Copyright (c) 2020, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# API base error class definition
#
# Date created: 10.06.2020
# Date last modified: 10.06.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.06
#
########################################################################################################################


class BaseError(Exception):
    """ API base error class

    This class definition serves as API base error class. It
    inherits from general Python Exception class.

    """

    ####################################################################################################################
    # Constructor method
    ####################################################################################################################

    def __init__(self, code=None, status=None, description=None, payload=None, message=None, traceback=None):
        """ Constructor method

        This method is the is constructor method for the API
        error handling base class

        Arguments:

            code (str): HTTP error code
            status (str): HTTP error status
            description (str): HTTP error description
            payload (str): Payload of the current request
            message (str): Individual message derived from the resource
            traceback (str): Error traceback

        """

        Exception.__init__(self)

        self.code = code
        self.description = description
        self.traceback = traceback
        self.status = status
        self.payload = payload
        self.message = message

    ####################################################################################################################
    # Method for returning a defined error dictionary
    ####################################################################################################################

    def to_dict(self):
        """ Creates the error message dictionary

        This method returns a pre-defined error dictionary with all necessary
        information about the occurred error. The "error_description" section
        contains already existing information about the error derived from the
        Werkzeuge HTTP exception class. The other information are specific to
        the error message.

        """

        return {
            "error_description": {
                "code": self.code,
                "status": self.status,
                "description": self.description
            },
            "error_definition": {
                "payload": self.payload,
                "message": self.message,
                "traceback": self.traceback
            }

        }
