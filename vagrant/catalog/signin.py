import requests
import uuid
from flask import request, flash, jsonify
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from catalog import app
from database_setup import User


##############################################################################
# Google+ Sign in/out
##############################################################################
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Handles G+ third-party signin."""
    code = request.get_json()['data']
    try:
        oauth_flow = flow_from_clientsecrets('clientsecrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange code for credentials object with token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return jsonify(message='Failed to upgrade authorization code'), 401

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
           .format(access_token))
    result = requests.get(url).json()
    # Abort if error.
    if result.get('error') is not None:
        return jsonify(message=result.get('error')), 500

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return jsonify(message="Token's user ID doesn't match login."), 401

    # Verify that the access token is valid for this app.
    app_token = ''.join(['494203108202-8qijkubc2hiio08dptgb5cc21su8qf84',
                         '.apps.googleusercontent.com'])
    if result['issued_to'] != app_token:
        return jsonify(message="Token's client ID does not match app's."), 401

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return jsonify(status='ok',
                       message='Current user is already connected.',
                       username=login_session['username'],
                       picture=login_session['picture'])

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    data = requests.get(userinfo_url, params=params).json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Get user id from database or add new user.
    user_rec = app.q_User().filter_by(name=data['name'],
                                      email=data['email']).first()
    if user_rec:
        login_session['user_id'] = user_rec.id
    else:
        new_user = User(name=data['name'],
                        email=data['email'],
                        picture=data['picture'])
        app.db_session.add(new_user)
        app.db_session.commit()
        login_session['user_id'] = new_user.id

    flash("you are now logged in as {}".format(login_session['username']))

    resp = jsonify(status='ok',
                   username=login_session['username'],
                   picture=login_session['picture'])
    resp.set_cookie('_csrf', _csrf(), max_age=None)
    return resp


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    """Handles G+ signout."""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token', None)
    if access_token is None:
        login_session.clear()
        return jsonify(error='Current user not connected.'), 401

    url = ('https://accounts.google.com/o/oauth2/revoke?token={}'
           .format(access_token))
    result = requests.get(url)

    if result.status_code == 200:
        # Reset the user's sesson.
        login_session.clear()
        resp = jsonify(status='ok', message='Successfully disconnected.')
        resp.set_cookie('_csrf', '', expires=0)
        return resp
    else:
        # For whatever reason, the given token was invalid.
        return jsonify(error='Failed to revoke token for given user.'), 400


##############################################################################
# CSRF
##############################################################################
def _csrf():
    """Create and return a new csrf state value.

    Creates a new *csrf* code and saves it in the *login_session*, then
    returns the code.

    :Returns: A 32-character string csrf code.
    """
    login_session['_csrf'] = uuid.uuid4().hex.upper()
    return login_session['_csrf']
