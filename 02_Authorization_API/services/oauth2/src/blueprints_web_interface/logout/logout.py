########################################################################################################################
#
# Copyright (c) 2019, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
# Logout definition
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Blueprint, session
from flask import redirect

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_logout = Blueprint('bp_logout', __name__)


########################################################################################################################
# Route definition for the logout scenario
########################################################################################################################

@bp_logout.route('/logout')
def logout():
    """ Logs out a user

    This methods logs out a user from the system by removing his
    or her session variable and redirecting him or her to the
    starting page.

    Returns:
        Redirects the user

    """

    del session['id']
    return redirect('/')
