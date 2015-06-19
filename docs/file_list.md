***`catalog_app.py`*** - Main program that runs the server side operations.

***`catalog_app_test.py`*** - Test suite for **catalog_app**.

***`catalog/__init__.py`*** - Package init file.

***`catalog/api.py`*** - Flask routing methods that return JSON data.

***`catalog/signin.py`*** - Flask routing methods for handling signin and signout
from Google+ and returns JSON data.

***`catalog/views.py`*** - Flask routing methods that return HTML pages.

***`catalog/database_setup.py`*** - When running this file, it deletes an existing database
and builds a new database with empty tables. Contains the database table information
and a method for getting a connection (`get_database_session()`).

***`catalog/fake_data.py`*** - Run this file to fill the database with fictional sample data.

***`static/js/ajax.js`*** - Contains a javascript method that simplifies a POST request.

***`static/js/signin.js`*** - Contains a javascript method for the google signin button.

***`templates/`*** - The `base.html` file contains the head and html code used by all
other files.  Other `*.html` files are inserted as the body to the `base.html` file.

***`website_mockup/`*** - Sample pages from the application saved as static
pages showing what the site would look like with a server connection.

___`*.rst`___ - *reStructuredText* files used in Sphinx documentation.

***`conf.py`*** - Configuration file for Sphinx documentation program.

***`make.bat`*** - Batch file for executing Sphinx documenting program.

***`sphinx_build/`*** - Contains the compiled documentation website.

***`clientsecrets.json`*** - File containing app authentication data for communicating
with the Google+ API.
