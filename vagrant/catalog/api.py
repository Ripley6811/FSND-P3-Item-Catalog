import pip  # For getting list of installed packages
from functools import wraps
from flask import request, jsonify, abort
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
# JSON RESPONSE API (Using jsonify)
##############################################################################
@app.route('/items', methods=['GET'])
def get_items():
    """Returns a list of all menu items for a restaurant.

    Items are sorted by overall popularity: number of 'favorite' ratings down
    to number of 'dislike' ratings. Each item also includes the user's rating
    if a user is logged in.
    """
    r_id = request.args['id']
    recs = app.q_MenuItem().filter_by(restaurant_id=r_id)

    # Convert to serializable and add logged-in user's ratings for each item.
    user_id = login_session.get('user_id', None)
    serializable_recs = []
    for each_rec in recs:
        srec = each_rec.sdict
        for each_rating in each_rec.ratings:
            if each_rating.user_id == user_id:
                srec['rating'] = each_rating.rating
                break
        else:
            srec['rating'] = 0
        serializable_recs.append(srec)

    # Sort menu items by their popularity and return list.
    resp = sorted(
        serializable_recs,
        key=lambda d: (-d['favorite_count'], -d['good_count'], d['bad_count'])
    )
    return jsonify(items=resp)


@app.route('/api/restaurants', methods=['GET'])
def api_restaurants():
    """Returns a list of restaurants in the database.

    :returns: JSON with a 'restaurants' key and list of restaurants.
    """
    recs = app.q_Restaurant().order_by('name')
    resp = [each.sdict for each in recs]
    return jsonify(restaurants=resp)


@app.route('/api/users', methods=['GET'])
def api_users():
    """Returns a list of users in the database.

    Email addresses are removed from returned data.

    :returns: JSON with a 'users' key and list of users.
    """
    recs = app.q_User().all()
    resp = [each.sdict for each in recs]
    [each.pop('email', None) for each in resp]
    return jsonify(users=resp)


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
        # Retrieve menu items by the given restaurant name.
        try:
            recs = app.q_MenuItem().join(Restaurant).filter_by(name=name)
        except NoResultFound:
            return jsonify(error='Restaurant not found.'), 400
        except MultipleResultsFound:
            resp = jsonify(error='Multiple restaurants found. Use ID instead.')
            return resp, 400
    else:
        # Retrieve menu items by the restaurant ID.
        recs = app.q_MenuItem().filter_by(restaurant_id=r_id)
    # Convert database objects to serializable dict objects.
    recs_json = [each.sdict for each in recs]
    return jsonify(menu=recs_json)


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
        try:
            user_id = int(request.args.get('user_id'))
        except ValueError as e:
            return abort(400)
    else:
        user_id = login_session.get('user_id', None)
    if user_id is not None:
        recs = app.q_Rating().filter_by(user_id=user_id, rating=1)
    else:
        return abort(400)
    count = recs.count()
    # Make a list of the serializable version of each rec.
    recs_json = [each.item.sdict for each in recs]
    # Return a random sampling of the items up to the limit.
    return jsonify(items=sample(recs_json, min(limit, count)))


@app.route('/ratings', methods=['POST'])
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


@app.route('/items', methods=['POST'])
@checks_login_and_csrf_status
def save_item():
    """Saves new food item to the database.

    Incoming request data must contain key-value pairs for new item.

    :Returns: JSON object with ID of new menu item or error message.
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
        return jsonify(id=new_rec.id)
    except IntegrityError as e:
        app.db_session.rollback()
        return jsonify(error=e.orig.pgerror), 500


@app.route('/items', methods=['PUT'])
@checks_login_and_csrf_status
def update_item():
    """Saves changes to an existing item.

    :Returns: JSON with item ID or error message.
    """
    user_id = login_session['user_id']
    obj = request.get_json()
    item = obj.pop('item')
    item_id = item['id']
    rating = int(obj.pop('rating', 0))
    # Try to update the item using it's ID.
    try:
        app.q_MenuItem().filter_by(id=item_id).update(item)
        app.db_session.flush()
    except IntegrityError as e:
        app.db_session.rollback()
        return jsonify(error=e.orig.pgerror), 500
    # Create or update rating if rating > 0.
    if rating:
        try:
            # Try update.
            rating_rec = app.q_Rating().filter_by(item_id=item_id,
                                                  user_id=user_id).one()
            rating_rec.rating = rating
            app.db_session.flush()
        except NoResultFound:
            # Create new rating record.
            new_rating = MenuItemRating(rating=rating,
                                        item_id=item_id,
                                        user_id=user_id)
            app.db_session.add(new_rating)
            app.db_session.flush()
    # Commit changes and return item ID for reference.
    app.db_session.commit()
    return jsonify(id=item_id)


@app.route('/restaurants', methods=['POST'])
@checks_login_and_csrf_status
def save_restaurant():
    """Saves new restaurant to the database.

    Incoming request data must contain key-value pairs for new item.

    :Returns: JSON object with ID of the new record or error message.
    """
    obj = request.get_json()
    restaurant_data = obj.pop('restaurant')
    try:
        new_rec = Restaurant(created_by=login_session['user_id'],
                             **restaurant_data)
        app.db_session.add(new_rec)
        app.db_session.flush()
        app.db_session.commit()
        return jsonify(id=new_rec.id)
    except IntegrityError:
        app.db_session.rollback()
        return jsonify(error='Restaurant save failed'), 500


@app.route('/restaurants', methods=['PUT'])
@checks_login_and_csrf_status
def update_restaurant():
    """Saves changes to an existing restaurant.

    :Returns: JSON with restaurant ID or error message.
    """
    obj = request.get_json()
    item = obj.pop('restaurant')
    if item.get('id', None):
        app.q_Restaurant().filter_by(id=item['id']).update(item)
        app.db_session.commit()
        return jsonify(id=item['id'])
    else:
        return jsonify(error='Restaurant update failed'), 500


@app.route('/items', methods=['DELETE'])
@checks_login_and_csrf_status
def delete_item():
    """Deletes an item from the database.

    :Returns: JSON object with status of 'ok' or HTML error message.
    """
    if 'id' not in request.get_json():
        return abort(400)
    if not isinstance(request.get_json()['id'], int):
        return abort(400)
    try:
        record = app.q_MenuItem().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok')
    except IntegrityError:
        app.db_session.rollback()
        return abort(500)


@app.route('/restaurants', methods=['DELETE'])
@checks_login_and_csrf_status
def delete_restaurant():
    """Deletes a restaurant from the database.

    :Returns: JSON object with status of 'ok' or HTML error message.
    """
    if 'id' not in request.get_json():
        return abort(400)
    if not isinstance(request.get_json()['id'], int):
        return abort(400)
    try:
        record = app.q_Restaurant().get(request.get_json()['id'])
        app.db_session.delete(record)
        app.db_session.commit()
        return jsonify(status='ok')
    except IntegrityError:
        app.db_session.rollback()
        return abort(500)


@app.route('/environment', methods=['GET'])
@checks_login_and_csrf_status
def show_environment():
    """Returns a list of installed packages on the server environment."""
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s == %s" % (i.key, i.version)
                                     for i in installed_packages])
    return jsonify(installed_packages=installed_packages_list)
