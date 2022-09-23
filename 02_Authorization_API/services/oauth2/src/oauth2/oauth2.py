########################################################################################################################
#
# OAuth2 functionalities, grant definitions, revocation and protected resources
#
# Date created: 19.09.2019
# Date last modified: 15.05.2020
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 20.05
#
########################################################################################################################

from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (create_query_client_func, create_save_token_func, create_revocation_endpoint,
                                       create_bearer_token_validator)
from authlib.oauth2.rfc6749 import grants
from init.init_database import db
from models.model_user import User
from models.model_oauth_client import OAuth2Client
from models.model_oauth_token import OAuth2Token


########################################################################################################################
# Password Grant class definition
########################################################################################################################

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):

    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()

        if user is not None and user.check_password(password):
            return user


########################################################################################################################
# Refresh Token Grant class definition
########################################################################################################################

class RefreshTokenGrant(grants.RefreshTokenGrant):

    def authenticate_refresh_token(self, refresh_token):
        token = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()

        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential):
        credential.revoked = True
        db.session.add(credential)
        db.session.commit()


########################################################################################################################
# Token revocation and protected resource definition
########################################################################################################################

query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization = AuthorizationServer(query_client=query_client, save_token=save_token)
require_oauth = ResourceProtector()


########################################################################################################################
# Method for adding all OAuth functionalities to flask app object
########################################################################################################################

def config_oauth(app):
    authorization.init_app(app)

    # support all grants
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
