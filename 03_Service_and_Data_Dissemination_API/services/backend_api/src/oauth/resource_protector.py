########################################################################################################################
#
# Implementation of an own Resource Protector
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from authlib.integrations.flask_oauth2 import ResourceProtector as _ResourceProtector
from authlib.oauth2 import OAuth2Error
from authlib.oauth2.rfc6749 import MissingAuthorizationError, HttpRequest
from error_classes.http_error_401.http_error_401 import UnauthorizedError
from error_classes.http_error_403.http_error_403 import ForbiddenError
from error_classes.http_error_500.http_error_500 import InternalServerErrorAPI
from flask import _app_ctx_stack, abort, request as _req
from flask.signals import Namespace
from init.app_constructor import app
import functools

########################################################################################################################
# OAuth signal definition
########################################################################################################################

_signal = Namespace()
client_authenticated = _signal.signal('client_authenticated')
token_revoked = _signal.signal('token_revoked')
token_authenticated = _signal.signal('token_authenticated')


########################################################################################################################
# class definition for the Resource Protector
########################################################################################################################

class ResourceProtector(_ResourceProtector):
    """ Class definition for an OAuth decorator

    This class defines a protecting method for resource servers. It is creating
    a "require_oauth" decorator easily with the definition of a ResourceProtector.

    """

    ####################################################################################################################
    # Method for raising the error message
    ####################################################################################################################

    def raise_error_response(self, error):
        """ Custom error response for OAuth2 errors

        This method raises an individual exception for OAuth2 errors. It is a re-implementation
        of the original method in order to customize the error response.

        Arguments:
            error (obj): OAuth2Error

        Raises:
            Exception depending one the status code

        """

        status = error.status_code
        body = dict(error.get_body())

        if status == 401:
            if 'error_description' in body:
                error = UnauthorizedError(f"{body['error']}: {body['error_description']}", "", "")

            else:
                error = UnauthorizedError(f"{body['error']}", "", "")

        elif status == 403:
            if 'error_description' in body:
                error = ForbiddenError(f"{body['error']}: {body['error_description']}", "", "")

            else:
                error = ForbiddenError(f"{body['error']}", "", "")

        else:
            error = InternalServerErrorAPI(f"{body['error']}: {body['error_description']}", "", "")
            abort(500, error.to_dict())

        abort(status, error.to_dict())

    ####################################################################################################################
    # Method for acquiring the token
    ####################################################################################################################

    def acquire_token(self, scope=None, operator=app.config['SCOPE_CONNECTOR']):
        """A method to acquire current valid token with the given scope.

        Arguments:
            scope (str, list): scope values
            operator (str): value of "AND" or "OR"

        Returns:
             token (obj): object
        """

        request = HttpRequest(
            _req.method,
            _req.full_path,
            _req.data,
            _req.headers
        )

        if not callable(operator):
            operator = operator.upper()
        token = self.validate_request(scope, request, operator)
        token_authenticated.send(self, token=token)
        ctx = _app_ctx_stack.top
        ctx.authlib_server_oauth2_token = token
        return token

    ####################################################################################################################
    # Method for defining the decorator object
    ####################################################################################################################

    def __call__(self, scope=None, operator=app.config['SCOPE_CONNECTOR'], optional=False):
        def wrapper(f):
            @functools.wraps(f)
            def decorated(*args, **kwargs):
                try:
                    self.acquire_token(scope, operator)
                except MissingAuthorizationError as error:
                    if optional:
                        return f(*args, **kwargs)
                    self.raise_error_response(error)
                except OAuth2Error as error:
                    self.raise_error_response(error)
                return f(*args, **kwargs)

            return decorated

        return wrapper
