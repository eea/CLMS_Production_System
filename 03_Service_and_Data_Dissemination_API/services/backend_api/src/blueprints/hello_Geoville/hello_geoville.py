########################################################################################################################
#
# Copyright (c) 2021, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is prohibited for all commercial
# applications without licensing by GeoVille GmbH.
#
# Index Page for the API Gateway
#
# Date created: 01.06.2020
# Date last modified: 07.07.2021
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 21.07
#
########################################################################################################################

from flask import Blueprint
import os
import pyfiglet

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

index_page = Blueprint('index_page', __name__)


########################################################################################################################
# Returns a static HTML page used as index page for API Gateway
########################################################################################################################

@index_page.route('/')
def api_hello_geoville():
    """ Returns static content for the index page

    This methods returns a static HTML page containing a nice figlet. The route is used to serve the index page of
    API Gateway.

    Returns:
        (str): static HTML contents

    """

    ascii_banner = pyfiglet.figlet_format("CLCplus Backbone API\r\n2021")

    html_text_pre = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">' \
                    '<head>' \
                        '<title>Welcome to the CLCplus Backbone Service API</title>' \
                        '<LINK REL="StyleSheet" href="style1.css" type="text/css">' \
                    '</head>' \
                    '<body>' \
                        '<h1>Welcome to the CLCplus Backbone Service API</h1>' \
                        '<pre class="ascii">'

    html_text_post = f'</pre><p>(V 21.08)</p></body>'

    static_content = html_text_pre + ascii_banner + html_text_post

    return static_content
