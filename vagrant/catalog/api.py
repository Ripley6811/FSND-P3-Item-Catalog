import pip # For getting list of installed packages
from functools import wraps
from flask import request, render_template, jsonify, redirect, url_for, abort
from flask import session as login_session
from catalog import app
from database_setup import Restaurant, MenuItem, MenuItemRating, User
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError
from random import sample



##############################################################################
# Decorators
##############################################################################
def authorize(func):
    """Decorator for first checking user login state before proceeding
    with function. Returns 401 unauthorized error if not logged in or csrf
    check fails.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check that user id exists in session
        if 'user_id' not in login_session:
            return abort(401)
        # Verify posted csrf token matches session token
        if request.get_json()['_csrf'] != login_session['_csrf']:
            return abort(401)
        return func(*args, **kwargs)
    return wrapper
    

##############################################################################
# JSON API (Using jsonify)
##############################################################################
@app.route('/get/items', methods=['POST'])
def get_items():
    """Returns a list of all menu items for a restaurant.
    
    Items are sorted by overall popularity: number of 'favorite' ratings down
    to number of 'dislike' ratings.
    """
    params = request.get_json()
    restaurant = app.db_session.query(Restaurant).filter_by(id = params['id']).first()
    recs = app.db_session.query(MenuItem).filter_by(restaurant_id = params['id'])
    # Order menu items by their popularity.
    resp = sorted(
        [each.sdict for each in recs], 
        key=lambda d: (-d['favorite_count'], -d['good_count'], d['bad_count'])
    )
    # Add logged-in user's ratings into the response for display.
    query = app.db_session.query(MenuItemRating)
    for each in resp:
        rec = query.filter_by(item_id = each['id'], 
                              user_id = login_session.get('user_id', None)).first()
        each['rating'] = rec.rating if rec else 0
    return jsonify(items=resp)


@app.route('/get/ratings', methods=['POST'])
def get_ratings():
    params = request.get_json()
    recs = app.db_session.query(MenuItemRating).filter_by(id = params['id']).all()
    resp = [each.sdict for each in recs]
    return jsonify(items=resp)


@app.route('/api/restaurants', methods=['GET'])
def api_restaurants():
    recs = app.db_session.query(Restaurant).all()
    resp = [each.sdict for each in recs]
    return jsonify(status='ok', restaurants=resp)


@app.route('/api/menu', methods=['GET'])
@app.route('/api/menu/restaurant=<string:name>', methods=['GET'])
@app.route('/api/menu/restaurant_id=<int:rid>', methods=['GET'])
def api_menu(name=None, rid=None):
    if 'restaurant_id' in request.args:
        rid = request.args.get('restaurant_id')
    if 'restaurant' in request.args:
        name = request.args.get('restaurant')
    if name:
        try:
            restaurant = app.db_session.query(Restaurant).filter_by(name = name).one()
            recs = app.db_session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
            recs_json = [each.sdict for each in recs]
            return jsonify(status='ok', menu=recs_json)
        except NoResultFound:
            return jsonify(status='error', error='Restaurant not found.')
        except MultipleResultsFound:
            return jsonify(status='error', error='Multiple restaurants found. Use ID instead of name.')
    elif rid != None:
        recs = app.db_session.query(MenuItem).filter_by(restaurant_id = rid)
        recs_json = [each.sdict for each in recs]
        if len(recs_json) > 0:
            return jsonify(status='ok', menu=recs_json)
        else:
            return jsonify(status='error', error='Menu items not found.')
    return jsonify(status='error', error='ID or name parameter not found in database')


@app.route('/api/favorites', methods=['GET', 'POST'])
def get_favorites(user_id=None):
    """Returns three random favorited menu items.
    
    Pass a user_id as a parameter or default to the currently logged in user.
    Returns an error if neither exists.
    
    :arg optional user_id: ID of user.
    """
    if 'user_id' in request.args:
        user_id = request.args.get('user_id')
    else:
        try:
            user_id = login_session['user_id']
        except KeyError as e:
            resp = jsonify(status='error', error='User not logged in.')
            resp.status_code = 400
            return resp
    q = app.db_session.query(MenuItemRating)
    recs = q.filter_by(user_id=user_id, rating = 1)
    count = recs.count()
    recs_json = [each.item.sdict for each in recs]
    return jsonify(items=sample(recs_json, min(3, count)))


@app.route('/save/rating', methods=['POST'])
@authorize
def save_rating():
    """Saves a menu item rating to the database."""
    params = request.get_json()
    params.pop('_csrf')
    try:
        new_rec = MenuItemRating(user_id=login_session['user_id'], **params)
    except KeyError:
        resp = jsonify(status='error', error='User is not logged in.')
        resp.status_code = 401
        return resp
    try:
        rec = app.db_session.query(MenuItemRating).filter_by(user_id=new_rec.user_id,
                                                      item_id=new_rec.item_id).one()
        if rec:
            rec.rating = new_rec.rating
            app.db_session.commit()
        return jsonify(status='ok')
    except NoResultFound:
        app.db_session.add(new_rec)
        app.db_session.commit()
        return jsonify(status='ok')
    
    


@app.route('/save/item', methods=['POST'])
@authorize
def save_item():
    """Saves new food item to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    :Returns:
        Response object with id of new menu item record.
    """
    obj = request.get_json()
    rating = int(obj.pop('rating', 0))
    try:
        new_rec = MenuItem(created_by=login_session['user_id'],
                           **obj.pop('item'))
        app.db_session.add(new_rec)
        app.db_session.commit()
        if rating:
            new_rating = MenuItemRating(rating=rating, 
                                        item_id=new_rec.id,
                                        user_id=login_session['user_id'])
            app.db_session.add(new_rating)
            app.db_session.commit()
        return jsonify(status='ok', id=new_rec.id)
    except IntegrityError as e:
        app.db_session.rollback()
        resp = jsonify(status='error', error=e.orig.pgerror) # Internal server error
        resp.status_code = 500
        return resp
    except KeyError:
        app.db_session.rollback()
        resp = jsonify(status='error', error='Must be logged in to make changes to the database.')
        resp.status_code = 401
        return resp

    
@app.route('/update/item', methods=['POST'])
@authorize
def update_item():
    """Saves changes to an existing item.
    
    :Returns: JSON with status of 'ok' or 'error' and message.
    """
    obj = request.get_json()
    item = obj.pop('item')
    rating = int(obj.pop('rating', 0))
    if item.get('id', None):
        app.db_session.query(MenuItem).filter_by(id=item['id']).update(item)
        app.db_session.commit()
    if rating:
        try:
            rating_rec = app.db_session.query(MenuItemRating) \
                                   .filter_by(item_id=item['id'],
                                              user_id=login_session['user_id']).one()
            rating_rec.rating = rating
            app.db_session.commit()
        except NoResultFound:
            new_rating = MenuItemRating(rating=rating, 
                                        item_id=item['id'],
                                        user_id=login_session['user_id'])
            app.db_session.add(new_rating)
            app.db_session.commit()
    return jsonify(status='ok')


@app.route('/save/restaurant', methods=['POST'])
@authorize
def save_restaurant():
    """Saves new restaurant to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    :Returns:
        Response object with id of the new record.
    """
    obj = request.get_json()
    restaurant_data = obj.pop('restaurant')
    try:
        new_rec = Restaurant(created_by=login_session['user_id'],
                             **restaurant_data)
        app.db_session.add(new_rec)
        app.db_session.flush()
        app.db_session.commit()
    except IntegrityError:
        app.db_session.rollback()
        res = jsonify(error='Menu item save failed') # Internal server error
        res.status_code = 500
        return res
    return jsonify(status='ok', id=new_rec.id)


@app.route('/delete/item', methods=['POST'])
@authorize
def delete_item():
    """Deletes an item from the database.
    
    Return:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return alert(400)
    try:
        record = app.db_session.query(MenuItem).get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok')
    except IntegrityError:
        app.db_session.rollback()
        return alert(500) # Internal server error
    

@app.route('/delete/restaurant', methods=['POST'])
@authorize
def delete_restaurant():
    """Deletes a restaurant from the database.
    
    Return:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return alert(400)
    try:
        record = app.db_session.query(Restaurant).get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok', url=url_for('restaurants'))
    except IntegrityError:
        app.db_session.rollback()
        return alert(500) # Internal server error


# From a suggestion on http://stackoverflow.com/questions/739993/how-can-i-get-a-list-of-locally-installed-python-modules
@app.route('/environment')
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
         for i in installed_packages])
    return jsonify(installed_packages=installed_packages_list)