########################################################################################################################
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# OAuth2 database model descriptions for SQLAlchemy
#
# Date created: 01.06.2020
# Date last modified: 10.02.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.02
#
########################################################################################################################

from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin, OAuth2TokenMixin
from flask_sqlalchemy import SQLAlchemy
from init.app_constructor import app
import time

########################################################################################################################
# Initialising the SQLAlchemy object
########################################################################################################################

db = SQLAlchemy(app)


########################################################################################################################
# Database model definition for the user table
########################################################################################################################

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password):
        return password == 'valid'


########################################################################################################################
# Database model definition for the OAuth2 client table
########################################################################################################################

class OAuth2Client(db.Model, OAuth2ClientMixin):

    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')


########################################################################################################################
# Database model definition for the OAuth2 token table
########################################################################################################################

class OAuth2Token(db.Model, OAuth2TokenMixin):

    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
