import unittest
from flask_testing import TestCase, LiveServerTestCase
import requests

from app import app, db

class MyTest(TestCase):
    
    def create_app(self):
        app.secret_key = 'secret_key'
        # Disable some built in error catching with the 'TESTING' flag.
        app.config['TESTING'] = True
        return app
    
    def setUp(self):
        print '---SETUP---'
        db.create_all(test=True)
        app.session = db.get_database_session(test=True)
        
    def tearDown(self):
        print '---CLOSE---'
        app.session.close()
        db.drop_all(test=True)
        
        
    def test_some_json(self):
        response = self.client.get("/environment")
        assert('packages' in response.json)
        

class MyLiveTest(LiveServerTestCase):
    
    def create_app(self):
        app.secret_key = 'secret_key'
        app.config['TESTING'] = True
        # Default port is 5000
        app.config['LIVESERVER_PORT'] = 8943
        return app
    
    def setUp(self):
        print '---SETUP---'
        db.create_all(test=True)
        app.session = db.get_database_session(test=True)
        
    def tearDown(self):
        print '---CLOSE---'
        app.session.close()
        db.drop_all(test=True)
    
    
    def test_server_is_up_and_running(self):
        print app.session.query(db.MenuItem).first()
        response = requests.get(self.get_server_url())
        print response
        self.assertEqual(response.status_code, 200)
        
        
if __name__ == '__main__':
    unittest.main()