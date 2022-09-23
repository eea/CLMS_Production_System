########################################################################################################################
#
# Starting point for the OAuth server
#
# Date created: 19.09.2019
# Date last modified: 21.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from init.init_app import app
from blueprints_api_interface.create_client.create_client import bp_create_client_api
from blueprints_api_interface.validate_token.validate_token import bp_validate_token
from blueprints_web_interface.create_client.create_client import bp_create_client
from blueprints_web_interface.index.index import bp_index
from blueprints_web_interface.logout.logout import bp_logout
from blueprints_web_interface.token_validation.token_validation import bp_token_validation
from blueprints_web_interface.revoke_token.revoke_token import bp_revoke
from blueprints_web_interface.generate_token.generate_token import bp_generate_token
from oauth2.oauth2 import config_oauth

########################################################################################################################
# Registers the all the different calls
########################################################################################################################

app.register_blueprint(bp_create_client)
app.register_blueprint(bp_index)
app.register_blueprint(bp_logout)
app.register_blueprint(bp_token_validation)
app.register_blueprint(bp_revoke)
app.register_blueprint(bp_generate_token)
app.register_blueprint(bp_create_client_api)
app.register_blueprint(bp_validate_token)

########################################################################################################################
# Configure the app with the all possible OAuth grants
########################################################################################################################

config_oauth(app)

########################################################################################################################
# Registers the all the different calls
########################################################################################################################

#app.run(host=app.config['HOST'] ,debug=app.config['DEBUG'], port=app.config['PORT'])
