from flask import Flask
import database_setup as db_setup
from database_setup import Restaurant, MenuItem, MenuItemRating, User

app = Flask(__name__)
# Sub-modules require Flask instance called `app`.
import catalog.views
import catalog.api
import catalog.signin


def start_session(test=False):
    """Gets a session (SQLAlchemy) with the database.

    Gets a new session with the testing or production database and assigns
    it to the global `session` variable. The session is also added as an
    attribute to 'app'. See `database_setup.py` for dbapi type and db tables.

    :arg boolean test: Boolean to use test DB instead of the production DB.
    """
    app.db_session = db_setup.get_database_session(test=test)

# Access start_session method using a reference to app.
app.start_session = start_session


##############################################################################
# Helper functions for shorthand querying.
##############################################################################
def q_Restaurant():
    """Return a new query object for database Restaurant class."""
    return app.db_session.query(Restaurant)
app.q_Restaurant = q_Restaurant


def q_MenuItem():
    """Return a new query object for database MenuItem class."""
    return app.db_session.query(MenuItem)
app.q_MenuItem = q_MenuItem


def q_Rating():
    """Return a new query object for database MenuItemRating class."""
    return app.db_session.query(MenuItemRating)
app.q_Rating = q_Rating


def q_User():
    """Return a new query object for database MenuItemRating class."""
    return app.db_session.query(User)
app.q_User = q_User
