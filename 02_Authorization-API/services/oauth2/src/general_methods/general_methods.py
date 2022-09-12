########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Methods used in several packages
#
# Date created: 19.09.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10
#
########################################################################################################################

from flask import session
from models.model_user import User


########################################################################################################################
# Method definition for returning the User ID for the API call
########################################################################################################################

def current_user_api_call():
    """ Returns the current user ID

    This method returns either the current user ID for the a user
    called "geoville" or the user ID received from a session variable.

    Returns:
        (str): User ID

    """

    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)

    else:

        return User.query.filter(User.username == 'geoville').first()


########################################################################################################################
# Method definition for returning the User ID for the Front-End call
########################################################################################################################

def current_user():
    """ Returns the current user ID

    This method returns either None or the user ID received
    from a session variable.

    Returns:
        (str): User ID

    """

    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)

    return None
