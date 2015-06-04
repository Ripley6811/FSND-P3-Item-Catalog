#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from functools import wraps
from flask import render_template, redirect, url_for, flash, request
from database_setup import Restaurant, MenuItem, MenuItemRating, User
#from sqlalchemy.orm.exc import NoResultFound
from flask import session as login_session

from catalog import app


##############################################################################
# Decorators
##############################################################################
def authorize(func):
    """Decorator for first checking user login state before proceeding
    with page load. Redirects browser to main page if not logged in.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('restaurants'))
        return func(*args, **kwargs)
    return wrapper

##############################################################################
# Render template - These app.routes respond with web pages.
###############################################################################
@app.route('/')
def restaurants():
    """Returns a public main page showing list of restaurants."""
    return render_template('index.html', title='Restaurants',
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''))


@app.route('/menu/<int:restaurant_id>')
def restaurant_view(restaurant_id):
    """Returns a public menu page showing a restaurant's menu items.
    
    Editing and rating buttons are invisible/disabled if user is not logged in.
    """
    restaurant = app.db_session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('menu.html', title='Menu',
                           restaurant=restaurant.sdict,
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/new/item/<int:restaurant_id>', methods=['GET', 'POST'])
@authorize
def new_item(restaurant_id):
    """Returns a **private** page for entering a new menu item for a restaurant.
    
    Redirects to restaurant list if user is not logged in.
    """
    item = None
    item_id = request.args.get('id', None)
    rating = request.args.get('rating', 0)
    if item_id:
        item = app.db_session.query(MenuItem).filter_by(id = item_id).one().sdict
    restaurant = app.db_session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('new_item.html', title='New Item',
                           restaurant=restaurant.sdict,
                           item=item,
                           rating=rating,
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/new/restaurant', methods=['GET', 'POST'])
@authorize
def new_restaurant():
    """Returns a **private** page for entering a new restaurant.
    
    Redirects to restaurant list if user is not logged in.
    """
    r_id = request.args.get('id', None)
    restaurant = app.db_session.query(Restaurant).filter_by(id = r_id).first()
    return render_template('new_restaurant.html', title='New Restaurant',
                           restaurant=restaurant.sdict if restaurant else None,
                           username=login_session.get('username', ''),
                           picture=login_session.get('picture', ''),
                           _csrf=_csrf())


@app.route('/random_favorites')
@authorize
def random_favorites():
    """Returns a **private** page displaying a random selection of user's favorites.
    
    Redirects to restaurant list if user is not logged in.
    """
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
    
    :Returns:
        A csrf code as a 32-character string.
    """
    login_session['_csrf'] = uuid.uuid4().hex.upper()
    return login_session['_csrf']

