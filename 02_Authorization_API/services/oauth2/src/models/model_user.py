########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Index Page for the API Gateway
#
# Date created: 19.09.2019
# Date last modified: 02.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10
#
########################################################################################################################

from init.init_app import bcrypt
from database.create_db_object import db


########################################################################################################################
# Database model definition for the User
########################################################################################################################

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(128), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password):

        if bcrypt.check_password_hash(self.password, password):
            return True

        else:
            return False
