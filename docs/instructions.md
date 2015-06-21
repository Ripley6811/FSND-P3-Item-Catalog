1. **Virtual Machine setup:**
    - Follow the instructions [here (on Udacity.com)](https://www.udacity.com/wiki/ud088/vagrant)
to set up the Vagrant virtual machine used in this project.

2. **Open project in Vagrant VM:**
    - Save this repository to disk and navigate to the `vagrant` directory.
From there, run `vagrant up` then `vagrant ssh` and that will bring you to the
VM prompt. Navigate to the `/vagrant/catalog` directory in VM.

3. **Database setup:**
    - The `database_setup.py` file contains all the code to set up the **resttest**
    database, tables and views. Run this file within the VM:
    ```ssh
    ...-trusty-32:/vagrant/catalog$ python database_setup.py
    ```
    You should see the database setup commands *echo* to the command terminal without
    error. The default is you add a postgresql database to the VM server. (There is
    a sqlite3 dbapi option by changing the value of **`use_postgresql`** but it is
    not thoroughly tested.)

4. **Add filler data:**
    - Preset data can be added to the database by following the setup with running
    the `fake_data.py` file within the VM:
    ```ssh
    ...-trusty-32:/vagrant/catalog$ python fake_data.py
    ```

3. **Run the server file:**
    - Run `catalog_app.py` from in the `vagrant` directory VM prompt:

    ```ssh
    ...-trusty-32:/vagrant$ python catalog_app.py
     * Running on http://0.0.0.0:8000/
     * Restarting with reloader
    ```

6. **Navigate to `http://localhost:8000`:**
    - The home page of website is at `http://localhost:8000` while the server (`catalog_app.py`)
is running.

8. **Website navigation**
    - The main page is a listing of restaurants. All pages will have a blue button
    that goes back to the home page restaurant list. Blue editing buttons, shown with
    a pencil image (Glyphicon) appear for each restaurant and each item only if
    a user is logged in.
    - There is a Google+ signin button at the top-right corner of all pages which
    changes to a logout button with user photo when logged in. Click this button
    to log in and log out.
    - Click on any restaurant row to view the saved items from that restaurant on another
    page. The menu page displays a list including price, description and the user's critique of the item.
    - Critique has three choices: A *heart* means it is a favorite item, *thumb up* means it is
    good and might get it again, and a *thumb down* means NEVER get it again!
    - Critiques and the ability to add/edit items and restaurants is reserved for
    logged in members. Look for blue buttons with a pencil image in the item row
    when logged in.
    - See "Urban Burger" restaurant to see how user critiques are aggregated and
    ordered (user critiques created in `fake_data.py`).

8. **Test the application:**
    - Install the **`Flask-Testing`** package with pip in the virtual environment
    if it doesn't already exist.
    You can go to `http://localhost:8000/environment` to see a list of installed
    packages in the VM or just run the test and see if it is missing.
    ```
    sudo pip install Flask-Testing
    ```
    Run the test suite file called `catalog_app_test.py` in the `vagrant` directory.
