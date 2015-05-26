#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import get_database_session, Restaurant, MenuItem
from sqlalchemy.exc import IntegrityError
from random import sample, choice
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

app = Flask(__name__)

# Get a connection session to the database.
# See `database_setup.py` for dbapi type and db tables.
session = get_database_session()


##############################################################################
# Render template
##############################################################################
@app.route('/')
def restaurants():
    _csrf = renew_csrf();
    return render_template('index.html', title='Restaurants', _csrf=_csrf)


@app.route('/random_favorites')
def random_favorites():
    _csrf = renew_csrf();
    return render_template('favorites.html', title='Favorites', _csrf=_csrf)


@app.route('/menu/<int:restaurant_id>/')
def restaurant_view(restaurant_id):
    _csrf = renew_csrf();
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('menu.html', title='Menu', _csrf=_csrf,
                           restaurant=restaurant.sdic)


@app.route('/new/item/<int:restaurant_id>/')
def new_item(restaurant_id):
    _csrf = renew_csrf();
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('new_item.html', title='New Item', _csrf=_csrf,
                           restaurant=restaurant.sdic)


@app.route('/new/restaurant')
def new_restaurant():
    _csrf = renew_csrf();
    return render_template('new_restaurant.html', title='New Restaurant', _csrf=_csrf)


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


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('_csrf') != login_session['_csrf']:
        return jsonify(status=401, message='Invalid state parameter')
    
    code = request.get_json()['data']
    try:
        oauth_flow = flow_from_clientsecrets('clientsecrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange code for credentials object with token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return jsonify(status=401, message='Failed to upgrade authorization code')
    
    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Abort if error.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        return response
    
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != '494203108202-8qijkubc2hiio08dptgb5cc21su8qf84.apps.googleusercontent.com':
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

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
    return jsonify(status=200, username=data['name'], picture=data['picture'])


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        login_session.pop('access_token')
        login_session.pop('gplus_id')
        login_session.pop('username')
        login_session.pop('email')
        login_session.pop('picture')
        return jsonify(status=401, message='Current user not connected.')
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        login_session.pop('access_token')
        login_session.pop('gplus_id')
        login_session.pop('username')
        login_session.pop('email')
        login_session.pop('picture')

        return jsonify(status=200, message='Successfully disconnected.')
    else:
        # For whatever reason, the given token was invalid.
        return jsonify(status=400, message='Failed to revoke token for given user.')


@app.route('/get/user_info', methods=['POST'])
def get_user_info():
    return jsonify(status=200,
                   username=login_session.get('username', ''),
                   picture=login_session.get('picture', ''))


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
