########################################################################################################################
#
# Encpoint for testing the OAuth Resource Protector functionality
#
# Date created: 07.10.2019
# Date last modified: 12.03.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.03
#
########################################################################################################################

from authlib.flask.oauth2 import current_token
from flask import Blueprint, jsonify
from oauth2.oauth2 import require_oauth

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_token_validation = Blueprint('bp_token_validation', __name__)


########################################################################################################################
# Route definition for testing the Resource Protector
########################################################################################################################

@bp_token_validation.route('/oauth/validate_token')
@require_oauth('validate')
def api_me():
    """ Checks if the resource protector works

    This methods is used to test if the defined scopes and resource
    protector works as expected.

    Returns:
        (dict): user ID and name to the corresponding token

    """

    client_id = current_token.client_id
    return jsonify(client_id=client_id)

