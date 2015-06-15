#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
from flask import render_template, redirect, url_for, flash, request
from database_setup import Restaurant, MenuItem, MenuItemRating, User
from flask import session as login_session

from catalog import app


##############################################################################
# Decorators
##############################################################################
def checks_authorization(func):
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
    context = {
        'title': 'Restaurants',
        'username': login_session.get('username', ''),
        'picture': login_session.get('picture', '')
    }
    return render_template('index.html', **context)


@app.route('/menu/<int:restaurant_id>')
def restaurant_view(restaurant_id):
    """Returns a public menu page showing a restaurant's menu items.

    Editing and rating buttons are invisible/disabled if user is not logged in.
    """
    restaurant = app.q_Restaurant().get(restaurant_id)
    context = {
        'title': 'Menu',
        'restaurant': restaurant.sdict,
        'username': login_session.get('username', ''),
        'picture': login_session.get('picture', '')
    }
    return render_template('menu.html', **context)


@app.route('/new/item/<int:restaurant_id>')
@checks_authorization
def new_item(restaurant_id):
    """Returns a **private** page for adding or editing a menu item.

    Redirects to restaurant list if user is not logged in.
    """
    item_id = request.args.get('id', None)
    rating = request.args.get('rating', 0)
    restaurant = app.q_Restaurant().get(restaurant_id)
    context = {
        'title': 'Edit Item' if item_id else 'New Item',
        'restaurant': restaurant.sdict,
        'item': None,
        'rating': rating,
        'username': login_session.get('username', ''),
        'picture': login_session.get('picture', '')
    }
    if item_id is not None:
        context['item'] = app.q_MenuItem().get(item_id).sdict
    return render_template('new_item.html', **context)


@app.route('/new/restaurant')
@checks_authorization
def new_restaurant():
    """Returns a **private** page for adding or editing a restaurant.

    Redirects to restaurant list if user is not logged in.
    """
    r_id = request.args.get('id', None)
    context = {
        'title': 'Edit Restaurant' if r_id else 'New Restaurant',
        'restaurant': None,
        'username': login_session.get('username', ''),
        'picture': login_session.get('picture', '')
    }
    if r_id is not None:
        context['restaurant'] = app.q_Restaurant().get(r_id).sdict
    return render_template('new_restaurant.html', **context)


@app.route('/random_favorites')
@checks_authorization
def random_favorites():
    """Returns a **private** page displaying a random selection of favorites.

    Redirects to restaurant list if user is not logged in.
    """
    context = {
        'title': 'Favorites',
        'username': login_session.get('username', ''),
        'picture': login_session.get('picture', '')
    }
    return render_template('favorites.html', **context)
