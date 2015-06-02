from flask import Flask
import database_setup as db

app = Flask(__name__)

import catalog.views
import catalog.api
import catalog.gsignin

def start_session(test=False):
    """Gets a session (SQLAlchemy) with the database.
    
    Gets a new session with the testing or production database and assigns
    it to the global `session` variable. The session is also added as an 
    attribute to 'app'. See `database_setup.py` for dbapi type and db tables.
    
    Args:
        test: Boolean to use test database instead of the production one.
    """
    app.db = db.get_database_session(test=test)

    
# Access start_session method using a reference to app.
app.start_session = start_session