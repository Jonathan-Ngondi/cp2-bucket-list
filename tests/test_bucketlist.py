import unittest
import json 
from app import create_app, db



class BucketListTestCases(unittest.TestCase):
    """This class represents the bucketlist test cases"""
       
    def setUp(self):
        """"Initialize the app and set up test variables."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = json.dumps({'name': 'Travels'})
        self.bucketlist_item = json.dumps({'bucketlist_item':'Go to Kyrat.'})
        self.user_details = json.dumps({"username":"Tester", "password1":"Function","password2":"Function", "email":"tester@example.com"})
        self.client().post('/api/v1/auth/register', data=self.user_details)
        self.user_login = json.dumps({"username":"Tester","password":"Function"})
        login = self.client().post('/api/v1/auth/login', data = self.user_login)
        json_login = json.loads(login.data)
        self.token = json_login['token']

        with self.app.app_context():
            db.create_all()

    def test_homepage_route(self):
        """Test the route /api/v1/"""
        
        request = self.client().get('/')
        self.assertEqual(request.status_code, 200)
     


    def test_login(self):
        """Tests that a user can be logged into the app and a token generated."""
        response = self.client().post('/api/v1/auth/login', data=self.user_login    )
        self.assertEqual(response.status_code, 200)
        json_dict = json.loads(response.data)
        self.assertIn(json_dict['User']['username'], "Tester")
    

    def test_login_with_bad_password(self):
        """Tests that a user with bad credentials can't be logged in."""
        user = json.dumps({'username': 'Tester',
                'password': 'Jabbafoo',
               })
        response = self.client().post('/api/v1/auth/login', data=user)
        self.assertEqual(response.status_code, 400)
        json_dict = json.loads(response.data)
        self.assertIn("There was a problem", json_dict['message'].decode('utf-8'))

    def test_auth_user_registration_with_not_matching_passwords(self):
        """Tests whether the api will reject a user with bad credentials."""
        user = json.dumps({'username':'ThiagoSilva',
                'email': 'Thiago@example.com',
                'password1': 'ElPisto12',
                'password2': 'ElPistolero'})
        response = self.client().post('/api/v1/auth/register', data=user)
        json_dict = json.loads(response.data)
        self.assertIn("Your passwords don't match", json_dict['message'].decode('utf-8'))
        self.assertEqual(response.status_code, 400)
    
    def test_register_user_regisration_of_existing_user(self):
        user = json.dumps({'username':'Tester',
                'email': 'tester@example.com',
                'password1': 'Function',
                'password2': 'Function'})
        response = self.client().post('/api/v1/auth/register', data=user)
        json_dict = json.loads(response.data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("That username already exists", json_dict['message'])
        
    def test_login_user_token_generated(self):
        """Test to ensure that a token is assigned when a user logs in"""
        response = self.client().post('api/v1/auth/login', data=self.user_login)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_bucketlist_creation(self):
        """"Test that the API can create a bucketlist (POST, request)"""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Travels', str(res.data))

    def test_get_bucketlists_can_get_all_bucketlists(self):
        """Test that the API can return a queryset of all the bucketlists."""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists', headers={"token":self.token})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Travels', str(res.data))


    def test_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/1', headers={"token":self.token})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Travels', str(res.data))

    def test_invalid_bucketlist_id(self):
        """Test API returns a bad request code for an invalid id."""
        res = self.client().get('/api/v1/bucketlists/23', headers={"token":self.token})
        self.assertEqual(res.status_code, 404)

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist item"""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().put('/api/v1/bucketlists/1', headers={"token":self.token}, data=json.dumps({"name": 'Memorable Experiences'}))
        self.assertEqual(resp.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/1', headers={"token":self.token})
        self.assertIn("Memorable Experiences", str(res.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/api/v1/bucketlists/1', headers={"token":self.token})
        self.assertEqual(res.status_code, 200)
        res = self.client().get('/bucketlists/1')
        self.assertEqual(res.status_code, 404)

    def test_bucketlist_delete_bad_id(self):
        """Test that a bad id deletion request yields a 400 error. """
        result = self.client().delete('/bucketlists/504')
        self.assertEqual(result.status_code, 404)

    def test_creation_new_item(self):
        """Tests that a user can add an item to a bucket list. (POST, data)"""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().post('/api/v1/bucketlists/1/items', headers={"token":self.token}, data=self.bucketlist_item)
        self.assertEqual(resp.status_code, 201)

    def test_modifying_bucketlist_item(self):
        """Tests that an item can be modified in a bucketlist."""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().post('/api/v1/bucketlists/1/items', headers={"token":self.token}, data=self.bucketlist_item)
        self.assertEqual(resp.status_code, 201)
        new_resp = json.dumps({"bucketlist_item":"Go to Spain."})
        put = self.client().put('/api/v1/bucketlists/1/items/1', headers={"token":self.token}, data = new_resp)
        self.assertEqual(put.status_code, 201)
    
    def test_delete_bucketlist_item(self):
        """Tests that an item can be deleted from a bucketlist."""
        res = self.client().post('/api/v1/bucketlists', headers={"token":self.token}, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().post('/api/v1/bucketlists/1/items', headers={"token":self.token}, data=self.bucketlist_item)
        self.assertEqual(resp.status_code, 201)
        res = self.client().delete('/api/v1/bucketlists/1/items/1', headers={"token":self.token})
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        """Tears down all test_db data and resets db to empty state"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    flask_testing.main()
