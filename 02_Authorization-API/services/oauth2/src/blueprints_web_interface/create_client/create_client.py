########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Create client API call for the front-end version
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Blueprint, request
from flask import render_template, redirect
from general_methods.general_methods import current_user
from init.init_database import db
from models.model_oauth_client import OAuth2Client
from werkzeug.security import gen_salt

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_create_client = Blueprint('bp_create_client', __name__)


########################################################################################################################
# Route definition the client creation
########################################################################################################################

@bp_create_client.route('/create_client', methods=('GET', 'POST'))
def create_client():
    """ Creates a new client in the database

    This methods redirects the current user to the starting page in
    case of a successful or failed insertion.

    Returns:
        Redirects the user

    """

    user = current_user()
    if not user:
        return redirect('/')

    if request.method == 'GET':
        return render_template('create_client.html')

    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)

    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''

    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return redirect('/')
