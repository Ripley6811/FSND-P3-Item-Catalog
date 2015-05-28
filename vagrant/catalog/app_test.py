import unittest
from flask_testing import TestCase, LiveServerTestCase
import json
import requests

from app import app, db
"""
Access the active session with `app.session`
Access the database table classes through `db`: 
   `db.MenuItem`, `db.Restaurant`, etc.
"""

class MyTestCase(TestCase):
    
    def create_app(self):
        app.secret_key = 'secret_key'
        # Disable some built in error catching with the 'TESTING' flag.
        app.config['TESTING'] = True
        return app
    
    def setUp(self):
        db.create_all(test=True)
        app.start_session(test=True)
        
    def tearDown(self):
        app.session.close()
        db.drop_all(test=True)


class TestPageLoading(MyTestCase):
    
    def test_main_page_load(self):
        response = self.client.get("/")
        self.assert200(response)

    def test_no_login_add_restaurant(self):
        response = self.client.get('/new/restaurant')
        self.assertRedirects(response, '/')

    def test_no_login_add_menu_item(self):
        response = self.client.get('/new/item/1/')
        self.assertRedirects(response, '/')

        
class TestJSONResponse(MyTestCase):
    
    def test_some_json(self):
        response = self.client.get("/environment")
        self.assertIsInstance(response.json, dict)
        self.assertIn('packages', response.json)
        

class TestDatabase(MyTestCase):
    r_data = dict(
        name= 'Area Critters',
        phone= '555-12345',
        note= "I'm a note"
    )
    mi_baddata = dict(
        name = 'Chicken Curry',
        description = 'In pesto sauce',
        price = '15.99',
        course = 'Entree',
    )
    
    def test_add_restaurant(self):
        # Insert record must return status 200 if successful.
        response = self.client.post('/save/restaurant', 
                                    data=json.dumps(self.r_data), 
                                    content_type='application/json')
        self.assert200(response, 'Save restaurant data post error')
        # Retrieve list of restuarants must have 1 record.
        response = self.client.post('/get/restaurants',
                                    content_type='application/json')
        self.assert200(response, 'Get restaurant json list error')
        self.assertEquals(len(response.json['restaurants']), 1)
        # Restaurant record data must match original data.
        r0 = response.json['restaurants'][0]
        self.assertIsInstance(r0.pop('id'), int)
        self.assertEquals(r0, self.r_data)
        
    def test_add_bad_restaurant(self):
        # Insert record must return status 500 if failure.
        r_baddata = self.r_data.copy()
        r_baddata.pop('name')
        response = self.client.post('/save/restaurant', 
                                    data=json.dumps(r_baddata), 
                                    content_type='application/json')
        self.assert500(response, 'Save restaurant data post did not fail')
    
    def test_add_menu_item_sans_restaurant(self):
        response = self.client.post('/save/item', 
                                    data=json.dumps(self.mi_baddata), 
                                    content_type='application/json')
        self.assert500(response, 'Bad insert did not return status code 500')
        
    def test_add_menu_item_with_restaurant(self):
        # Add restaurant
        response = self.client.post('/save/restaurant', 
                                    data=json.dumps(self.r_data), 
                                    content_type='application/json')
        self.assert200(response, 'Save restaurant data post error')
        # Create good menu entry with `id` from previous response.
        mi_data = self.mi_baddata
        restaurant_id = response.json['id']
        mi_data['restaurant_id'] = restaurant_id
        # Insert new menu item record.
        response = self.client.post('/save/item', 
                                    data=json.dumps(self.mi_baddata), 
                                    content_type='application/json')
        self.assert200(response, 'Did not return successful status code')
        # Retrieve list of menu items for restaurant.
        response = self.client.post('/get/items',
                                    data=json.dumps({'id': restaurant_id}),
                                    content_type='application/json')
        self.assert200(response, 'Get menu item json list error')
        self.assertEquals(len(response.json['items']), 1)
        r0 = response.json['items'][0]
        # Pop and check attributes that the database added.
        self.assertIsInstance(r0.pop('id'), int)
        self.assertIsInstance(r0.pop('restaurant_name'), unicode)
        self.assertIn(r0.pop('rating'), [0,1,2,3])
        # Compare other data with original data.
        self.assertEquals(r0, mi_data)
        
        
class MyLiveTest(LiveServerTestCase):
    
    def create_app(self):
        app.secret_key = 'secret_key'
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 8888 # Default is 5000
        return app
    
    def setUp(self):
        db.create_all(test=True)
        app.start_session(test=True)
        
    def tearDown(self):
        app.session.close()
        db.drop_all(test=True)
    
    
    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        self.assertEqual(response.status_code, 200)
        
        
if __name__ == '__main__':
    unittest.main()
    
""" Testing API Reference:
Most assert methods are inherited from `unittest`. Additional methods unique
to `flask_testing` are provided with and without underscores.

Results from dir(TestCase)
--------------------------
addCleanup
addTypeEqualityFunc
assert200
assert400
assert401
assert403
assert404
assert405
assert500
assertAlmostEqual
assertAlmostEquals
assertContext
assertDictContainsSubset
assertDictEqual
assertEqual
assertEquals
assertFalse
assertGreater
assertGreaterEqual
assertIn
assertIs
assertIsInstance
assertIsNone
assertIsNot
assertIsNotNone
assertItemsEqual
assertLess
assertLessEqual
assertListEqual
assertMultiLineEqual
assertNotAlmostEqual
assertNotAlmostEquals
assertNotEqual
assertNotEquals
assertNotIn
assertNotIsInstance
assertNotRegexpMatches
assertRaises
assertRaisesRegexp
assertRedirects
assertRegexpMatches
assertSequenceEqual
assertSetEqual
assertStatus
assertTemplateUsed
assertTrue
assertTupleEqual
assert_
assert_200
assert_400
assert_401
assert_403
assert_404
assert_405
assert_500
assert_context
assert_redirects
assert_status
assert_template_used
countTestCases
create_app
debug
defaultTestResult
doCleanups
fail
failIf
failIfAlmostEqual
failIfEqual
failUnless
failUnlessAlmostEqual
failUnlessEqual
failUnlessRaises
failureException
get_context_variable
id
longMessage
maxDiff
render_templates
run
run_gc_after_test
setUp
setUpClass
shortDescription
skipTest
tearDown
tearDownClass



Results from dir(LiveServerTestCase)
------------------------------------
addCleanup
addTypeEqualityFunc
assertAlmostEqual
assertAlmostEquals
assertDictContainsSubset
assertDictEqual
assertEqual
assertEquals
assertFalse
assertGreater
assertGreaterEqual
assertIn
assertIs
assertIsInstance
assertIsNone
assertIsNot
assertIsNotNone
assertItemsEqual
assertLess
assertLessEqual
assertListEqual
assertMultiLineEqual
assertNotAlmostEqual
assertNotAlmostEquals
assertNotEqual
assertNotEquals
assertNotIn
assertNotIsInstance
assertNotRegexpMatches
assertRaises
assertRaisesRegexp
assertRegexpMatches
assertSequenceEqual
assertSetEqual
assertTrue
assertTupleEqual
assert_
countTestCases
create_app
debug
defaultTestResult
doCleanups
fail
failIf
failIfAlmostEqual
failIfEqual
failUnless
failUnlessAlmostEqual
failUnlessEqual
failUnlessRaises
failureException
get_server_url
id
longMessage
maxDiff
run
setUp
setUpClass
shortDescription
skipTest
tearDown
tearDownClass
"""