########################################################################################################################
#
# Create client endpoint
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Blueprint, request
from general_methods.general_methods import current_user_api_call
from init.init_database import db
from models.model_oauth_client import OAuth2Client
from werkzeug.security import gen_salt

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_create_client_api = Blueprint('bp_create_client_api', __name__)


########################################################################################################################
# Route definition for creating a new client
########################################################################################################################

@bp_create_client_api.route('/oauth/create_client', methods=['POST'])
def create_client():
    """ Creates a new client in the database

    This methods returns a Python dictionary containing either an
    error message or client ID and a client secret, created during
    the insertion operation for a new client.

    Returns:
        (dict): message about the success of the creation

    """

    try:
        user = current_user_api_call()
        client = OAuth2Client(**request.form.to_dict(flat=True))
        client.user_id = user.id
        client.client_id = gen_salt(24)

        if client.token_endpoint_auth_method == 'none':
            client.client_secret = ''

        else:
            client.client_secret = gen_salt(48)

        db.session.add(client)
        db.session.commit()

        return {"client_id": client.client_id, "client_secret": client.client_secret}, 200

    except Exception as err:
        return {"error": f"Error communicating with the Authorization Server: {err}"}, 500
