from catalog import app
import uuid

"""
Item Catalog project main app.

Run this file as 'python catalog_app.py' to initialize the server.

Before running this app, ensure that the database is setup by running
'database_setup.py'.

Adding initial fake data is optional by running 'fake_data.py'.

Project repository and more details at:
https://github.com/Ripley6811/FSND-P3-Item-Catalog
"""

app.start_session()
app.secret_key = uuid.uuid4().hex  # 'secret_key'
app.run(host='0.0.0.0', port=8000, debug=True)
