# FSND-P3-Item-Catalog

> Restaurant menu database exercise using the Flask microframework and Knockout.js with a PostgreSQL VM server.

* [Summary](#summary)
* [Required Packages](#required-packages)
* [File List](#file-list)
* [Instructions](#instructions)
* [References](#references)


## Summary
Fullstack project built using Flask with a PostgreSQL database on a virtual machine.

This is a website that saves restaurant menu information along with a review system
for helping people remember what was good or bad at various restaurants. It also
features a randomized recommendation system using a person's favorite in case they
need help deciding where to go eat.

It was built using the Flask microframework connected to a PostgreSQL database, 
the KnockoutJS MVVM for a dynamic front-end, and Google+ third-party login
system (OAuth2).

Author: Jay W Johnson

[Link to GitHub repository](https://github.com/Ripley6811/FSND-P3-Item-Catalog)


## Required Packages
- [**Flask**](http://flask.pocoo.org/) - Python web framework
- [**SQLAlchemy**](http://www.sqlalchemy.org/) - Python SQL Toolkit and ORM
- [**Psycopg**](http://initd.org/psycopg/) - PostgreSQL adapter for Python



## File List
***`app.py`*** - Main program that runs the server side operations.

***`database_setup.py`*** - When running this file, it deletes an existing database
and builds a new database with empty tables. Contains the database table information
and a method for getting a connection (`get_database_session()`).

***`fake_data.py`*** - Run this file to fill the database with fictional sample data.

***`static/js/ajax.js`*** - Contains a javascript method that simplifies a POST request.

***`static/js/signin.js`*** - Contains a javascript method for the google signin button.

***`templates/`*** - The `base.html` file contains the head and html code used by all
other files.  Other `*.html` files are inserted as the body to the `base.html` file.



## Instructions
1. **Virtual Machine setup:** 
Follow the instructions [here (on Udacity.com)](https://www.udacity.com/wiki/ud088/vagrant)
to set up the Vagrant virtual machine used in this project.

2. **Open project in Vagrant VM:**
Save this repository to disk and navigate to the `vagrant` directory.
From there, run `vagrant up` then `vagrant ssh` and that will bring you to the
VM prompt. Navigate to the `/vagrant/catalog` directory in VM.

3. **Database setup:** 
The `database_setup.py` file contains all the code to set up the **resttest** 
database, tables and views. Run this file within the VM:
    ```ssh
    ...-trusty-32:/vagrant/catalog$ python database_setup.py
    ``` 
You should see the database setup commands *echo* to the command terminal without
error. The default is you add a postgresql database to the VM server. If you want
to use local directory database with the sqlite dbapi, then change **`use_postgresql`**
to **`False`** inside the *database_setup.py* file before running all files.

4. **Add filler data:**
Preset data can be added to the database by following the setup with running
the `fake_data.py` file within the VM:
    ```ssh
    ...-trusty-32:/vagrant/catalog$ python fake_data.py
    ``` 
    
3. **Run the server file:** 
Run `app.py` from virtual machine prompt:

    ```ssh
    ...-trusty-32:/vagrant/tournament$ python app.py
    Connected to PostgreSQL: resttest
     * Running on http://0.0.0.0:8000/
     * Restarting with reloader
    Connected to PostgreSQL: resttest
    ```

6. **Navigate to `http://localhost:8000`:**
The home page of website is at `http://localhost:8000` while the server (`app.py`) 
is running.

7. **Test the application:**





## References
***Stackoverflow.com***

- [Create database programmatically](http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy)
- [Delete file if exists with Python](http://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist)
- [Select a few from list](http://stackoverflow.com/questions/1262955/how-do-i-pick-2-random-items-from-a-python-set)
- [Need to flush() to get new record id](http://stackoverflow.com/questions/620610/sqlalchemy-obtain-primary-key-with-autoincrement-before-commit)
- [Credentials not serializable error fix](http://stackoverflow.com/questions/22915461/google-login-server-side-flow-storing-credentials-python-examples/22930708#22930708)



***SQLAlchemy.org***

- [Connecting and using PostgreSQL](http://docs.sqlalchemy.org/en/rel_1_0/dialects/postgresql.html?highlight=postgresql#dialect-postgresql)



***Jinja.pocoo.org***

- [How to use templates](http://jinja.pocoo.org/docs/dev/templates/)



***Knockoutjs.com***

- [Has-focus option](http://knockoutjs.com/documentation/hasfocus-binding.html)
- [Show item index in foreach loop](http://knockoutjs.com/documentation/foreach-binding.html)



***Developers.google.com***

- [Add sign-in button](https://developers.google.com/+/web/signin/add-button)



***Udacity.com***

- [Authentication & Authorization course](https://www.udacity.com/course/viewer#!/c-ud330-nd/l-3967218625/e-3963648623/m-4044308696)



***Gruntjs.com***

- [Getting started guide for Grunt](http://gruntjs.com/getting-started)



***NPMjs.com***

- [Grunt-Readme guide](https://www.npmjs.com/package/grunt-readme)




