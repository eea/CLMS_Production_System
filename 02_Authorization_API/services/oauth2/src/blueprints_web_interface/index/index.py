########################################################################################################################
#
# Index page definition
#
# Date created: 07.10.2019
# Date last modified: 15.10.2019
#
# __author__  = Michel Schwandner (schwandner@geoville.com)
# __version__ = 19.10.1
#
########################################################################################################################

from flask import Blueprint, request, session
from flask import render_template, redirect
from general_methods.general_methods import current_user
from init.init_app import bcrypt
from init.init_database import db
from models.model_user import User
from models.model_oauth_client import OAuth2Client

########################################################################################################################
# Creation of the blueprint
########################################################################################################################

bp_index = Blueprint('bp_index', __name__)


########################################################################################################################
# Route definition creating a new user
########################################################################################################################

@bp_index.route('/', methods=('GET', 'POST'))
def index():
    """ Creates a new user in the database

    This methods creates new user in the database and redirects
    him or her to the home page. If the user already exists and
    the password check is successful, the user will be redirected
    to the home page.

    Returns:
        Redirects the user to the home page

    """

    if request.method == 'POST':
        username = request.form.get('username')
        pw = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username=username, password=bcrypt.generate_password_hash(pw).decode('utf-8'))
            db.session.add(user)
            db.session.commit()
            session['id'] = user.id
            return redirect('/')

        else:
            if user.check_password(pw):
                session['id'] = user.id
                return redirect('/')

            else:
                return render_template('home.html')

    user = current_user()

    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()

    else:
        clients = []

    return render_template('home.html', user=user, clients=clients)
