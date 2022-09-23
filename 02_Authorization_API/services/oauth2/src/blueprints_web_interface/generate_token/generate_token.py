########################################################################################################################
#
# Generate token endpoint
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Blueprint
from oauth2.oauth2 import authorization

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_generate_token = Blueprint('bp_generate_token', __name__)


########################################################################################################################
# Route definition for token generation endpoint
########################################################################################################################

@bp_generate_token.route('/oauth/generate_token', methods=['POST'])
def issue_token():
    """ Issues a new token for a client

    This method returns the bearer and refresh token for an
    incoming request, if the client ID and secret are valid.

    Returns:
        (dict): bearer and refresh token

    """
    return authorization.create_token_response()
