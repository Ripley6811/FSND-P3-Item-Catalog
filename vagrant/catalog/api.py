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
def check_login_and_csrf_status(func):
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
# Helper functions for shorthand querying.
##############################################################################
def q_Restaurant():
    """Return a new query object for database Restaurant class."""
    return app.db_session.query(Restaurant)

def q_MenuItem():
    """Return a new query object for database MenuItem class."""
    return app.db_session.query(MenuItem)

def q_Rating():
    """Return a new query object for database MenuItemRating class."""
    return app.db_session.query(MenuItemRating)

def q_User():
    """Return a new query object for database MenuItemRating class."""
    return app.db_session.query(User)
    

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
    restaurant = q_Restaurant().filter_by(id = params['id']).first()
    recs = q_MenuItem().filter_by(restaurant_id = params['id'])
    # Order menu items by their popularity.
    resp = sorted(
        [each.sdict for each in recs], 
        key=lambda d: (-d['favorite_count'], -d['good_count'], d['bad_count'])
    )
    # Add logged-in user's ratings into the response for display.
    for each in resp:
        user_id = login_session.get('user_id', None)
        query = q_Rating().filter_by(item_id = each['id'], 
                                     user_id = user_id)
        rec = query.first()
        each['rating'] = rec.rating if rec else 0
    return jsonify(items=resp)


#@app.route('/get/ratings', methods=['POST'])
#def get_ratings():
#    params = request.get_json()
#    recs = q_Rating().filter_by(id = params['id']).all()
#    resp = [each.sdict for each in recs]
#    return jsonify(items=resp)


@app.route('/api/restaurants', methods=['GET'])
def api_restaurants():
    """Returns a list of restaurants in the database.
    
    :returns: JSON with a 'restaurants' key and list of restaurants.
    """
    recs = q_Restaurant().order_by('name').all()
    resp = [each.sdict for each in recs]
    return jsonify(status='ok', restaurants=resp)


@app.route('/api/users', methods=['GET'])
def api_users():
    """Returns a list of users in the database.
    
    Email addresses are removed from returned data.
    
    :returns: JSON with a 'users' key and list of users.
    """
    recs = q_User().all()
    resp = [each.sdict for each in recs]
    [each.pop('email', None) for each in resp]
    return jsonify(status='ok', users=resp)


@app.route('/api/menu', methods=['GET'])
@app.route('/api/menu/restaurant=<string:name>', methods=['GET'])
@app.route('/api/menu/restaurant_id=<int:rid>', methods=['GET'])
def api_menu(name=None, rid=None):
    """Returns the menu for a restaurant in JSON format.
    
    Requires either the name or an database ID number for a restaurant.
    You can get a list of restaurant names and ID numbers by using 
    "/api/restaurants".
    
    :arg string restaurant: The name of a restaurant to lookup.
    :arg int restaurant_id: The database ID of a restaurant.
    :returns: JSON with a 'menu' key and a list of menu items.
    """
    if 'restaurant_id' in request.args:
        rid = request.args.get('restaurant_id')
    if 'restaurant' in request.args:
        name = request.args.get('restaurant')
    if name:
        try:
            restaurant = q_Restaurant().filter_by(name = name).one()
            recs = q_MenuItem().filter_by(restaurant_id = restaurant.id)
            recs_json = [each.sdict for each in recs]
            return jsonify(status='ok', menu=recs_json)
        except NoResultFound:
            return jsonify(status='error', error='Restaurant not found.')
        except MultipleResultsFound:
            return jsonify(status='error', 
                error='Multiple restaurants found. Use ID instead of name.')
    elif rid != None:
        recs = q_MenuItem().filter_by(restaurant_id = rid)
        recs_json = [each.sdict for each in recs]
        if len(recs_json) > 0:
            return jsonify(status='ok', menu=recs_json)
        else:
            return jsonify(status='error', error='Menu items not found.')
    return jsonify(status='error', 
                   error='ID or name parameter not found in database')


@app.route('/api/favorites', methods=['GET', 'POST'])
def get_favorites(user_id=None, limit=3):
    """Returns three random favorited menu items.
    
    Pass a user_id as a parameter or default to the currently logged in user.
    Returns an error if neither exists.
    
    :arg optional user_id: ID of user.
    :arg optional limit: Maximum number of items to return.
    :returns: JSON with an 'items' key and a list of menu items.
    """
    print limit
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
    if 'user_id' in request.args:
        user_id = int(request.args.get('user_id'))
    else:
        try:
            user_id = login_session['user_id']
        except KeyError as e:
            resp = jsonify(status='error', error='User not logged in.')
            resp.status_code = 400
            return resp
    recs = q_Rating().filter_by(user_id=user_id, rating = 1)
    count = recs.count()
    recs_json = [each.item.sdict for each in recs]
    return jsonify(items=sample(recs_json, min(limit, count)))


@app.route('/save/rating', methods=['POST'])
@check_login_and_csrf_status
def save_rating():
    """Saves a menu item rating to the database.
    
    :Returns: The status of the database submission as JSON.
    """
    params = request.get_json()
    params.pop('_csrf')
    try:
        new_rec = MenuItemRating(user_id=login_session['user_id'], **params)
    except KeyError:
        resp = jsonify(status='error', error='User is not logged in.')
        resp.status_code = 401
        return resp
    try:
        query = q_Rating().filter_by(user_id=new_rec.user_id,
                                     item_id=new_rec.item_id)
        rec = query.one()
        if rec:
            rec.rating = new_rec.rating
            app.db_session.commit()
        return jsonify(status='ok')
    except NoResultFound:
        app.db_session.add(new_rec)
        app.db_session.commit()
        return jsonify(status='ok')
    
    


@app.route('/save/item', methods=['POST'])
@check_login_and_csrf_status
def save_item():
    """Saves new food item to the database.
    
    Incoming request data must contain key-value pairs for new item.
    
    :Returns:
        Response object with id of new menu item record as JSON.
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
        resp = jsonify(status='error', error=e.orig.pgerror)
        resp.status_code = 500
        return resp
    except KeyError:
        app.db_session.rollback()
        resp = jsonify(status='error', 
                       error='Must be logged in to make database changes.')
        resp.status_code = 401
        return resp

    
@app.route('/update/item', methods=['POST'])
@check_login_and_csrf_status
def update_item():
    """Saves changes to an existing item.
    
    :Returns: JSON with status of 'ok' or 'error' and message.
    """
    obj = request.get_json()
    item = obj.pop('item')
    rating = int(obj.pop('rating', 0))
    if item.get('id', None):
        q_MenuItem().filter_by(id=item['id']).update(item)
        app.db_session.commit()
    if rating:
        try:
            query = q_Rating().filter_by(item_id=item['id'],
                                         user_id=login_session['user_id'])
            rating_rec = query.one()
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
@check_login_and_csrf_status
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
        return jsonify(status='ok', id=new_rec.id)
    except IntegrityError:
        app.db_session.rollback()
        res = jsonify(error='Menu item save failed') # Internal server error
        res.status_code = 500
        return res
    

    
@app.route('/update/restaurant', methods=['POST'])
@check_login_and_csrf_status
def update_restaurant():
    """Saves changes to an existing restaurant.
    
    :Returns: JSON with status of 'ok' or 'error' and message.
    """
    obj = request.get_json()
    item = obj.pop('restaurant')
    if item.get('id', None):
        q_Restaurant().filter_by(id=item['id']).update(item)
        app.db_session.commit()
        return jsonify(status='ok', id=item['id'])


@app.route('/delete/item', methods=['POST'])
@check_login_and_csrf_status
def delete_item():
    """Deletes an item from the database.
    
    :Returns:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return alert(400)
    try:
        record = q_MenuItem().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok')
    except IntegrityError:
        app.db_session.rollback()
        return alert(500) # Internal server error
    

@app.route('/delete/restaurant', methods=['POST'])
@check_login_and_csrf_status
def delete_restaurant():
    """Deletes a restaurant from the database.
    
    :Returns:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return alert(400)
    try:
        record = q_Restaurant().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok', url=url_for('restaurants'))
    except IntegrityError:
        app.db_session.rollback()
        return alert(500) # Internal server error


# From a suggestion on http://stackoverflow.com/questions/739993/how-can-i-get-a-list-of-locally-installed-python-modules
@app.route('/api/environment', methods=['GET'])
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
         for i in installed_packages])
    return jsonify(installed_packages=installed_packages_list)