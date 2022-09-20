########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# OAuth2 method collection for the GEMS API
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.integrations.sqla_oauth2 import (create_query_client_func, create_save_token_func,
                                              create_revocation_endpoint, create_bearer_token_validator)
from oauth.oauth_models import db, OAuth2Client, OAuth2Token
from oauth.resource_protector import ResourceProtector

########################################################################################################################
# Setting up additional parameters
########################################################################################################################

query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization = AuthorizationServer(query_client=query_client, save_token=save_token, )
require_oauth = ResourceProtector()


########################################################################################################################
# Method for configuring the Flask app object
########################################################################################################################

def config_oauth(app):
    """ Configures the FLASK app

    This method registers the OAuth2 instance on the FLASK app object. Thus, all OAuth2 functionalities can be accessed
    through the FLASk app.

    Arguments:
        app (obj): FLASK app object

    """

    # initialise app
    authorization.init_app(app)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
