from flask import Flask, render_template, request, redirect, url_for, flash
from database_setup import get_database_session, Restaurant, MenuItem

app = Flask(__name__)

# Get a connection session to the database.
# See `database_setup.py` for dbapi type and db tables.
session = get_database_session()


@app.route('/')
#@app.route('/restaurants/<int:restaurant_id>/' methods=['GET','POST'])
def restaurantMenu():
#    return 'I\'m in!'
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    response = ''
    for item in items:
        response += item.name
        response += '<br>'
    return response

if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
