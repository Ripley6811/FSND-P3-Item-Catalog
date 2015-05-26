#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import get_database_session, Restaurant, MenuItem
from sqlalchemy.exc import IntegrityError
from random import sample

app = Flask(__name__)

# Get a connection session to the database.
# See `database_setup.py` for dbapi type and db tables.
session = get_database_session()


@app.route('/')
def restaurants():
    return render_template('index.html', title='Restaurants')


@app.route('/random_favorites')
def random_favorites():
    return render_template('favorites.html', title='Favorites')


@app.route('/menu/<int:restaurant_id>/')
def restaurant_view(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('menu.html', title='Menu',
                           restaurant=restaurant.sdic)


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
    resp = [item.sdic for item in items]
    return jsonify(items=sample(resp, 3))
    


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


@app.route('/new/item/<int:restaurant_id>/')
def new_item(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).first()
    return render_template('new_item.html', title='New Item', restaurant=restaurant.sdic)


@app.route('/new/restaurant')
def new_restaurant():
    return render_template('new_restaurant.html', title='New Restaurant')


@app.route('/update/item', methods=['POST'])
def update_item():
    params = request.get_json()
    session.query(MenuItem).filter_by(id = params['id']).update({'rating':params['rating']})
    session.commit()
    item = session.query(MenuItem).get(params['id'])
    return jsonify(status=200, item=item.sdic)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
