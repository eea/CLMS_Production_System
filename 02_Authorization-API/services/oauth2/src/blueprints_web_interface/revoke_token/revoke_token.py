########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Revoke token endpoint
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

bp_revoke = Blueprint('bp_revoke', __name__)


########################################################################################################################
# Route definition revoking the token
########################################################################################################################

@bp_revoke.route('/oauth/revoke_token', methods=['POST'])
def revoke_token():
    """ Revokes the token validity for a user

    This methods revokes the validity for specified token. Mostly
    called in combination with a log out procedure.

    Returns:
        (dict): message about successful revocation

    """

    return authorization.create_endpoint_response('revocation')