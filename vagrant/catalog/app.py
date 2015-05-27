#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pip
#import json
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database_setup as db
from database_setup import Restaurant, MenuItem
from sqlalchemy.exc import IntegrityError
from random import sample, choice
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
#import httplib2
from flask import make_response
import requests

app = Flask(__name__)

# Get a connection session to the database.
# See `database_setup.py` for dbapi type and db tables.
session = db.get_database_session()


##############################################################################
# Render template
##############################################################################
@app.route('/')
def restaurants():
    if 'username' not in login_session:
        _csrf = renew_csrf();
    return render_template('index.html', title='Restaurants')


@app.route('/menu/<int:restaurant_id>/')
def restaurant_view(restaurant_id):
    if 'username' not in login_session:
        _csrf = renew_csrf();
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('menu.html', title='Menu',
                           restaurant=restaurant.sdic)


@app.route('/new/item/<int:restaurant_id>/')
def new_item(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('new_item.html', title='New Item',
                           restaurant=restaurant.sdic)


@app.route('/new/restaurant')
def new_restaurant():
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    return render_template('new_restaurant.html', title='New Restaurant')


@app.route('/random_favorites')
def random_favorites():
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    return render_template('favorites.html', title='Favorites')


##############################################################################
# Jsonify
##############################################################################
@app.route('/get/items', methods=['POST'])
def get_items():
    params = request.get_json()
    restaurant = session.query(Restaurant).filter_by(id = params['id']).first()
    items = session.query(MenuItem).filter_by(restaurant_id = params['id'])
    resp = [item.sdic for item in items]

    return jsonify(items=resp)


@app.route('/get/restaurants', methods=['POST'])
def get_restaurants():
    records = session.query(Restaurant).all()
    resp = [r.sdic for r in records]
    return jsonify(restaurants=resp)


@app.route('/get/favorites', methods=['POST'])
def get_favorites():
    """Returns three random favorited menu items."""
    items = session.query(MenuItem).filter_by(rating = 1)
    count = items.count()
    resp = [item.sdic for item in items]
    return jsonify(items=sample(resp, min(3, count)))
    


@app.route('/save/item', methods=['POST'])
def save_item():
    """Saves new food item to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    Return:
        Response object with status of 200 if successful or 500 if failed.
    """
    try:
        session.add(MenuItem(**request.get_json()))
        session.commit()
    except IntegrityError:
        session.rollback()
        return jsonify(status=500) # Internal server error
    return jsonify(status=200)


@app.route('/save/restaurant', methods=['POST'])
def save_restaurant():
    """Saves new restaurant to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    Return:
        Response object with status of 200 if successful or 500 if failed.
        Also returns the id of the new record.
    """
    try:
        new_rec = Restaurant(**request.get_json())
        session.add(new_rec)
        session.flush()
        session.commit()
    except IntegrityError:
        session.rollback()
        return jsonify(status=500) # Internal server error
    return jsonify(status=200, id=new_rec.id)


@app.route('/delete/item', methods=['POST'])
def delete_item():
    """Deletes an item from the database.
    
    Return:
        Response object with status of 200 if successful or 500 if failed.
    """
#    try:
    record = session.query(MenuItem).get(request.form['id'])
    session.delete(record)
    session.commit()
#    except IntegrityError:
#        session.rollback()
#        return jsonify(status=500) # Internal server error
    
    return jsonify(status=200)


@app.route('/delete/restaurant', methods=['POST'])
def delete_restaurant():
    """Deletes a restaurant from the database.
    
    Return:
        Response object with status of 200 if successful or 500 if failed.
    """
#    try:
    record = session.query(Restaurant).get(request.get_json()['id'])
    session.delete(record)
    session.commit()
#    except IntegrityError:
#        session.rollback()
#        return jsonify(status=500) # Internal server error
    
    return jsonify(status=200)


@app.route('/update/item', methods=['POST'])
def update_item():
    params = request.get_json()
    session.query(MenuItem).filter_by(id = params['id']).update({'rating':params['rating']})
    session.commit()
    item = session.query(MenuItem).get(params['id'])
    return jsonify(status=200, item=item.sdic)


def renew_csrf():
    _csrf = ''.join(choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['_csrf'] = _csrf
    return _csrf


@app.route('/csrf', methods=['POST'])
def get_csrf():
    return jsonify(csrf=login_session['_csrf'])


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('_csrf') != login_session['_csrf']:
        res = jsonify(message='Invalid state parameter')
        res.status_code = 401
        return res
    
    code = request.get_json()['data']
    try:
        oauth_flow = flow_from_clientsecrets('clientsecrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange code for credentials object with token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        res = jsonify(message='Failed to upgrade authorization code')
        res.status_code = 401
        return res
    
    # Check that access token is valid
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token)
    result = requests.get(url).json()
    # Abort if error.
    if result.get('error') is not None:
        res = jsonify(message=result.get('error'))
        res.status_code = 500
        return res
    
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        res = jsonify(message="Token's user ID doesn't match given user ID.")
        res.status_code = 401
        return res

    # Verify that the access token is valid for this app.
    if result['issued_to'] != '494203108202-8qijkubc2hiio08dptgb5cc21su8qf84.apps.googleusercontent.com':
        res = jsonify(message="Token's client ID does not match app's.")
        res.status_code = 401
        return res

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return jsonify(message='Current user is already connected.')

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
            
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    flash("you are now logged in as {}".format(login_session['username']))
    return jsonify(status='ok', username=data['name'], picture=data['picture'])


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
#    login_session.clear()
    # Only disconnect a connected user.
    access_token = login_session.get('access_token', None)
    if access_token is None:
        login_session.clear()
        response = jsonify(message='Current user not connected.')
        response.status_code = 401
        return response
    
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    result = requests.get(url)
    
    if result.status_code == 200:
        # Reset the user's sesson.
        login_session.clear()
        return jsonify(status='ok', message='Successfully disconnected.')
    else:
        # For whatever reason, the given token was invalid.
        return jsonify(status=400, message='Failed to revoke token for given user.')


@app.route('/get/user_info', methods=['POST'])
def get_user_info():
    return jsonify(status=200,
                   username=login_session.get('username', ''),
                   picture=login_session.get('picture', ''))


# From a suggestion on http://stackoverflow.com/questions/739993/how-can-i-get-a-list-of-locally-installed-python-modules
@app.route('/environment')
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
         for i in installed_packages])
    return jsonify(packages=installed_packages_list)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(host='0.0.0.0', port=8000, debug=True)
