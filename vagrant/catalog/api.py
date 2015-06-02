from flask import request, render_template, jsonify, redirect, url_for
from flask import session as login_session
from catalog import app
from database_setup import Restaurant, MenuItem, MenuItemRating, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from random import sample





##############################################################################
# JSON API (Using jsonify)
##############################################################################
@app.route('/get/items', methods=['POST'])
def get_items():
    params = request.get_json()
    restaurant = app.db.query(Restaurant).filter_by(id = params['id']).first()
    recs = app.db.query(MenuItem).filter_by(restaurant_id = params['id'])
    
    resp = [each.sdict for each in recs]
    query = app.db.query(MenuItemRating)
    for each in resp:
        rec = query.filter_by(item_id = each['id'], 
                              user_id = login_session.get('user_id', None)).first()
        if rec:
            each['rating'] = rec.rating
        else:
            each['rating'] = 0
    return jsonify(items=resp)


@app.route('/get/ratings', methods=['POST'])
def get_ratings():
    params = request.get_json()
    recs = app.db.query(MenuItemRating).filter_by(id = params['id']).all()
    resp = [each.sdict for each in recs]
    return jsonify(items=resp)


@app.route('/get/restaurants', methods=['POST'])
def get_restaurants():
    recs = app.db.query(Restaurant).all()
    resp = [each.sdict for each in recs]
    return jsonify(restaurants=resp)


@app.route('/api/restaurants', methods=['GET'])
def api_restaurants():
    recs = app.db.query(Restaurant).all()
    resp = [each.sdict for each in recs]
    return jsonify(status='ok', restaurants=resp)


@app.route('/api/menu/restaurant=<string:name>', methods=['GET'])
@app.route('/api/menu/restaurant_id=<int:rid>', methods=['GET'])
def api_menu(name=None, rid=None):
    if name:
        restaurant = app.db.query(Restaurant).filter_by(name = name).first()
        if restaurant:
            recs = app.db.query(MenuItem).filter_by(restaurant_id = restaurant.id)
            recs_json = [each.sdict for each in recs]
            return jsonify(status='ok', menu=recs_json)
        else:
            return jsonify(status='error', error='Restaurant not found.')
    elif rid != None:
        recs = app.db.query(MenuItem).filter_by(restaurant_id = rid)
        recs_json = [each.sdict for each in recs]
        if len(recs_json) > 0:
            return jsonify(status='ok', menu=recs_json)
        else:
            return jsonify(status='error', error='Menu items not found.')


@app.route('/get/favorites', methods=['POST'])
def get_favorites():
    """Returns three random favorited menu items."""
    q = app.db.query(MenuItemRating)
    recs = q.filter_by(user_id=login_session['user_id'], rating = 1)
    count = recs.count()
    recs_json = [each.item.sdict for each in recs]
    return jsonify(items=sample(recs_json, min(3, count)))


@app.route('/save/rating', methods=['POST'])
def save_rating():
    """Saves a menu item rating to the database."""
    try:
        new_rec = MenuItemRating(user_id=login_session['user_id'], **request.get_json())
    except KeyError:
        resp = jsonify(status='failure', error='User is not logged in.')
        resp.status_code = 401
        return resp
    try:
        rec = app.db.query(MenuItemRating).filter_by(user_id=new_rec.user_id,
                                                      item_id=new_rec.item_id).one()
        if rec:
            rec.rating = new_rec.rating
            app.db.commit()
        return jsonify(status='ok')
    except NoResultFound:
        app.db.add(new_rec)
        app.db.commit()
        return jsonify(status='ok')
    
    


@app.route('/save/item', methods=['POST'])
def save_item():
    """Saves new food item to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    Return:
        Response object with id of new record.
    """
    try:
        new_rec = MenuItem(**request.get_json())
        app.db.add(new_rec)
        app.db.commit()
    except IntegrityError:
        app.db.rollback()
        resp = jsonify(message='Menu item save failed') # Internal server error
        resp.status_code = 500
        return resp
    return jsonify(id=new_rec.id)


@app.route('/save/restaurant', methods=['POST'])
def save_restaurant():
    """Saves new restaurant to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    Return:
        Response object with id of the new record.
    """
    try:
        new_rec = Restaurant(**request.get_json())
        app.db.add(new_rec)
        app.db.flush()
        app.db.commit()
    except IntegrityError:
        app.db.rollback()
        res = jsonify(message='Menu item save failed') # Internal server error
        res.status_code = 500
        return res
    return jsonify(id=new_rec.id)


@app.route('/delete/item', methods=['POST'])
def delete_item():
    """Deletes an item from the database.
    
    Return:
        Response object with status of 'ok'.
    """
#    try:
    record = app.db.query(MenuItem).get(request.form['id'])
    app.db.delete(record)
    app.db.commit()
#    except IntegrityError:
#        app.db.rollback()
#        return jsonify(status=500) # Internal server error
    
    return jsonify(status='ok')


@app.route('/delete/restaurant', methods=['POST'])
def delete_restaurant():
    """Deletes a restaurant from the database.
    
    Return:
        Response object with status of 'ok'.
    """
#    try:
    record = app.db.query(Restaurant).get(request.get_json()['id'])
    app.db.delete(record)
    app.db.commit()
#    except IntegrityError:
#        app.db.rollback()
#        return jsonify(status=500) # Internal server error
    
    return jsonify(status='ok', url=url_for('restaurants'))


#@app.route('/update/item', methods=['POST'])
#def update_item():
#    params = request.get_json()
#    app.db.query(MenuItem).filter_by(id = params['id']).update({'rating':params['rating']})
#    app.db.commit()
#    item = app.db.query(MenuItem).get(params['id'])
#    return jsonify(status='ok', item=item.sdict)

# From a suggestion on http://stackoverflow.com/questions/739993/how-can-i-get-a-list-of-locally-installed-python-modules
@app.route('/environment')
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
         for i in installed_packages])
    return jsonify(installed_packages=installed_packages_list)