***`app.py`*** - Main program that runs the server side operations.

***`database_setup.py`*** - When running this file, it deletes an existing database
and builds a new database with empty tables. Contains the database table information
and a method for getting a connection (`get_database_session()`).

***`fake_data.py`*** - Run this file to fill the database with fictional sample data.

***`static/js/ajax.js`*** - Contains a javascript method that simplifies a POST request.

***`static/js/signin.js`*** - Contains a javascript method for the google signin button.

***`templates/`*** - The `base.html` file contains the head and html code used by all
other files.  Other `*.html` files are inserted as the body to the `base.html` file.

***`website_mockup`*** - Sample pages from the application showing what it would
look like with a server connection.