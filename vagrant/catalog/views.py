#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import pip
import uuid
from flask import render_template, redirect, url_for, flash
#import database_setup as db
from database_setup import Restaurant, MenuItem, MenuItemRating, User
#from sqlalchemy.exc import IntegrityError
#from sqlalchemy.orm.exc import NoResultFound
from flask import session as login_session
#from flask import make_response
#import requests


from catalog import app


##############################################################################
# Render template
###############################################################################
@app.route('/')
def restaurants():
    """Public main page showing list of restaurants."""
    return render_template('index.html', title='Restaurants',
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''))


@app.route('/menu/<int:restaurant_id>/')
def restaurant_view(restaurant_id):
    """Public menu page showing a restaurant's menu items."""
    restaurant = app.db.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('menu.html', title='Menu',
                           restaurant=restaurant.sdict,
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/new/item/<int:restaurant_id>/')
def new_item(restaurant_id):
    """Private page for entering a new menu item for a restaurant."""
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    restaurant = app.db.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('new_item.html', title='New Item',
                           restaurant=restaurant.sdict,
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/new/restaurant')
def new_restaurant():
    """Private page for entering a new restaurant."""
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    return render_template('new_restaurant.html', title='New Restaurant',
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/random_favorites')
def random_favorites():
    """Private page returning a random selection of user's favorites."""
    if 'username' not in login_session:
        return redirect(url_for('restaurants'))
    return render_template('favorites.html', title='Favorites',
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''))




##############################################################################
# Authentication and CSRF
##############################################################################
def _csrf():
    """Create and return a new csrf state value.
    
    Creates a new *csrf* code and saves it in the *login_session*, then 
    returns the code.
    
    Return:
        A csrf code as a 32-character string.
    """
    login_session['_csrf'] = uuid.uuid4().hex.upper()
    return login_session['_csrf']


#if __name__ == '__main__':
#    start_session()
#    app.secret_key = uuid.uuid4().hex # 'secret_key'
#    app.run(host='0.0.0.0', port=8000, debug=True)
