import pip  # For getting list of installed packages
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
def checks_login_and_csrf_status(func):
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
        if request.cookies['_csrf'] != login_session['_csrf']:
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
    restaurant = app.q_Restaurant().filter_by(id=params['id']).first()
    recs = app.q_MenuItem().filter_by(restaurant_id=params['id'])
    # Order menu items by their popularity.
    resp = sorted(
        [each.sdict for each in recs],
        key=lambda d: (-d['favorite_count'], -d['good_count'], d['bad_count'])
    )
    # Add logged-in user's ratings into the response for display.
    for each in resp:
        user_id = login_session.get('user_id', None)
        query = app.q_Rating().filter_by(item_id=each['id'],
                                     user_id=user_id)
        rec = query.first()
        each['rating'] = rec.rating if rec else 0
    return jsonify(items=resp)


@app.route('/api/restaurants', methods=['GET'])
def api_restaurants():
    """Returns a list of restaurants in the database.

    :returns: JSON with a 'restaurants' key and list of restaurants.
    """
    recs = app.q_Restaurant().order_by('name').all()
    resp = [each.sdict for each in recs]
    return jsonify(status='ok', restaurants=resp)


@app.route('/api/users', methods=['GET'])
def api_users():
    """Returns a list of users in the database.

    Email addresses are removed from returned data.

    :returns: JSON with a 'users' key and list of users.
    """
    recs = app.q_User().all()
    resp = [each.sdict for each in recs]
    [each.pop('email', None) for each in resp]
    return jsonify(status='ok', users=resp)


@app.route('/api/menu', methods=['GET'])
@app.route('/api/menu/restaurant=<string:name>', methods=['GET'])
@app.route('/api/menu/restaurant_id=<int:r_id>', methods=['GET'])
def api_menu(name=None, r_id=None):
    """Returns the menu for a restaurant in JSON format.

    Requires either the name or database ID number for a restaurant.
    You can get a list of restaurant names and ID numbers by using
    "/api/restaurants".

    :arg string restaurant: The name of a restaurant to lookup.
    :arg int restaurant_id: The database ID of a restaurant.
    :returns: JSON with a 'menu' key and a list of menu items.
    """
    if 'restaurant_id' in request.args:
        r_id = request.args.get('restaurant_id')
    if 'restaurant' in request.args:
        name = request.args.get('restaurant')
    if name:
        # Retrieve restaurant ID in database with the given name.
        try:
            record = app.q_Restaurant().filter_by(name=name).one()
        except NoResultFound:
            return jsonify(error='Restaurant not found.'), 400
        except MultipleResultsFound:
            resp = jsonify(error='Multiple restaurants found. Use ID instead.')
            return resp, 400
        else:
            r_id = record.id
    recs = app.q_MenuItem().filter_by(restaurant_id=r_id)
    # Convert database objects to serializable dict objects.
    recs_json = [each.sdict for each in recs]
    return jsonify(status='ok', menu=recs_json)


@app.route('/api/favorites', methods=['GET'])
def get_favorites(user_id=None, limit=3):
    """Returns random selection of favorited menu items (default is three).

    Pass a user_id as a parameter or default to the currently logged in user.
    Returns an error if neither exists.

    :arg optional user_id: ID of user.
    :arg optional limit: Maximum number of items to return.
    :returns: JSON with an 'items' key and a list of menu items.
    """
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
    if 'user_id' in request.args:
        user_id = int(request.args.get('user_id'))
    else:
        try:
            user_id = login_session['user_id']
        except KeyError as e:
            return jsonify(status='error', error='User ID not found.'), 400
    recs = app.q_Rating().filter_by(user_id=user_id, rating=1)
    count = recs.count()
    # Make a list of the serializable version of each rec.
    recs_json = [each.item.sdict for each in recs]
    # Return a random sampling of the recs up to the limit.
    return jsonify(items=sample(recs_json, min(limit, count))), 501


@app.route('/save/rating', methods=['POST'])
@checks_login_and_csrf_status
def save_rating():
    """Saves a menu item rating to the database.

    :Returns: The status of the database submission as JSON.
    """
    user_id = login_session['user_id']
    # Retrieve and check parameters.
    params = request.get_json()
    try:
        item_id = params['item_id']
        new_rating = params['rating']
    except KeyError:
        return jsonify(error='Missing data in request.'), 400
    try:
        # Find existing rating record. Throws NoResultFound if none.
        rec = app.q_Rating().filter_by(user_id=user_id,
                                       item_id=item_id).one()
        rec.rating = new_rating
    except NoResultFound:
        # Add new rating record to database.
        new_rec = MenuItemRating(user_id=user_id,
                                 item_id=item_id,
                                 rating=new_rating)
        app.db_session.add(new_rec)
    app.db_session.commit()
    return jsonify(status='ok')


@app.route('/save/item', methods=['POST'])
@checks_login_and_csrf_status
def save_item():
    """Saves new food item to the database.

    Incoming request data must contain key-value pairs for new item.

    :Returns:
        Response object with id of new menu item record as JSON.
    """
    user_id = login_session['user_id']
    obj = request.get_json()
    rating = int(obj.pop('rating', 0))
    try:
        new_rec = MenuItem(created_by=user_id,
                           **obj.pop('item'))
        app.db_session.add(new_rec)
        app.db_session.flush()
        if rating:
            new_rating = MenuItemRating(rating=rating,
                                        item_id=new_rec.id,
                                        user_id=user_id)
            app.db_session.add(new_rating)
            app.db_session.commit()
        return jsonify(status='ok', id=new_rec.id)
    except IntegrityError as e:
        app.db_session.rollback()
        return jsonify(status='error', error=e.orig.pgerror), 500


@app.route('/update/item', methods=['POST'])
@checks_login_and_csrf_status
def update_item():
    """Saves changes to an existing item.

    :Returns: JSON with status of 'ok' or 'error' and message.
    """
    user_id = login_session['user_id']
    obj = request.get_json()
    item = obj.pop('item')
    item_id = item['id']
    rating = int(obj.pop('rating', 0))
    if item.get('id', None):
        app.q_MenuItem().filter_by(id=item_id).update(item)
        app.db_session.flush()
    if rating:
        try:
            query = app.q_Rating().filter_by(item_id=item_id,
                                             user_id=user_id)
            rating_rec = query.one()
            rating_rec.rating = rating
            app.db_session.flush()
        except NoResultFound:
            new_rating = MenuItemRating(rating=rating,
                                        item_id=item_id,
                                        user_id=user_id)
            app.db_session.add(new_rating)
            app.db_session.flush()
    app.db_session.commit()
    return jsonify(status='ok')


@app.route('/save/restaurant', methods=['POST'])
@checks_login_and_csrf_status
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
        return jsonify(error='Menu item save failed'), 500


@app.route('/update/restaurant', methods=['POST'])
@checks_login_and_csrf_status
def update_restaurant():
    """Saves changes to an existing restaurant.

    :Returns: JSON with status of 'ok' or 'error' and message.
    """
    obj = request.get_json()
    item = obj.pop('restaurant')
    if item.get('id', None):
        app.q_Restaurant().filter_by(id=item['id']).update(item)
        app.db_session.commit()
        return jsonify(status='ok', id=item['id'])


@app.route('/delete/item', methods=['POST'])
@checks_login_and_csrf_status
def delete_item():
    """Deletes an item from the database.

    :Returns:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return abort(400)
    try:
        record = app.q_MenuItem().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok')
    except IntegrityError:
        app.db_session.rollback()
        return abort(500)  # Internal server error


@app.route('/delete/restaurant', methods=['POST'])
@checks_login_and_csrf_status
def delete_restaurant():
    """Deletes a restaurant from the database.

    :Returns:
        Response object with status of 'ok'.
    """
    if 'id' not in request.get_json():
        return abort(400)
    try:
        record = app.q_Restaurant().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok', url=url_for('restaurants'))
    except IntegrityError:
        app.db_session.rollback()
        return abort(500)  # Internal server error


@app.route('/api/environment', methods=['GET'])
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
                                     for i in installed_packages])
    return jsonify(installed_packages=installed_packages_list)
