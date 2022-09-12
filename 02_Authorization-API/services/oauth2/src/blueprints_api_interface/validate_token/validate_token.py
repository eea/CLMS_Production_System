########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Validate token endpoint
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from authlib.flask.oauth2 import current_token
from flask import Blueprint, jsonify, request
from oauth2.oauth2 import require_oauth

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_validate_token = Blueprint('bp_validate_token', __name__)


########################################################################################################################
# Route definition for the validate token route
########################################################################################################################

@bp_validate_token.route('/oauth/validate_token')
@require_oauth()
def validate_token():
    """ Validates if a token is correct

    This methods returns a Python dictionary containing an error
    message and a status. Depending on those the information, the
    client can validate the API call.

    Returns:
       (dict): message about the success of the validation

    """
    try:
        req_data = request.json

        if not req_data['client_id']:
            return jsonify(error="Client ID is not contained in the request", status=False), 400

        if req_data['client_id'] == current_token.client_id:
            return jsonify(error=None, status=True), 200

        else:
            return jsonify(error="Token and user does not match", status=False), 400

    except Exception as err:
        return jsonify(error=f"Unknown error: {err}", status=False), 500
