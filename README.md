rdb-fullstack
=============

Fullstack project built with Flask and a PostgreSQL database on a virtual machine.


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
to **`False`** inside the *database_setup.py* file

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
[Create database programmatically](http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy)
[Delete file if exists with Python](http://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist)


***SQLAlchemy.org**
[Connecting and using PostgreSQL](http://docs.sqlalchemy.org/en/rel_1_0/dialects/postgresql.html?highlight=postgresql#dialect-postgresql)