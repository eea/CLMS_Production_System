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

from database.create_db_object import db
from authlib.flask.oauth2.sqla import OAuth2ClientMixin


########################################################################################################################
# Database model defintion
########################################################################################################################

class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')