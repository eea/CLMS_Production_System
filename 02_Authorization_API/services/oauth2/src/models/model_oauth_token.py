########################################################################################################################
#
# Index Page for the API Gateway
#
# Date created: 19.09.2019
# Date last modified: 28.09.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.09
#
########################################################################################################################

from authlib.flask.oauth2.sqla import OAuth2TokenMixin
from database.create_db_object import db
import time


########################################################################################################################
# Database model defintion
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
