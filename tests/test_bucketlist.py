import unittest
from flask_testing import TestCase
import os
import json 
from app import create_app, db
from app.v1.models import User


class BucketListTestCases(unittest.TestCase):
    """This class represents the bucketlist test cases"""
       
    def setUp(self):
        """"Initialize the app and set up test variables."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go to Molo for vacation'}
        self.user_details = {"username":"Tester", "password1":"Function","password2":"Function", "email":"tester@example.com"}
        self.user_login = {"username":"Tester","password":"Function"}
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
        self.assertIn(response.data,(''))
    

    def test_login_with_bad_password(self):
        """Tests that a user with bad credentials can't be logged in."""
        user = {'username': 'JonBones',
                'password': 'Jabbafoo',
               }
        response = self.client().post('/api/v1/auth/login', data=user)
        self.assertEqual(response.status_code, 201)

    def test_auth_user_registration_with_bad_credentials(self):
        """Tests whether the api will reject a user with bad credentials."""
        user = {'username':'ThiagoSilva',
                'email': 'Thiago@example.com',
                'password': 'ElPisto12',
                'password2': 'ElPistolero'}
        response = self.client().post('/api/v1/auth/register', data=user)
        self.assertEqual(response.status_code, 400)

    def test_token_authentication(self):
        """Test to ensure that a token is assigned when a user logs in"""
        user = {'username': 'JonBones',
                'password': 'Jabbafoo',
               }
        user_json = json.dumps(user)
        response = self.client().post('api/v1/auth/login', body=user_json)
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.body, 'token')

    def test_auth_user_registration(self):
        """Test that a new user can be registered and it generates a token."""
        user = {'username':'ThiagoSilva',
                'email': 'Thiago@example.com',
                'password': 'ElPistolero',
                'password2': 'ElPistolero'}
        response = self.client().post('api/v1/auth/register', data=user)
        self.assertEqual(response.status_code, 302)

    def test_bucketlist_creation(self):
        """"Test that the API can create a bucketlist (POST, request)"""
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Molo', str(res.data))

    def test_prevents_bucketlist_that_exists(self):
        """ Test that the API prevents bucketlists that have already been created from being
            created twice.
        """
        self.client().post('/bucketlists/', data=self.bucketlist)
        resp2 = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(resp2.status_code, 400)


    def test_can_get_all_bucketlists(self):
        """Test that the API can return a queryset of all the bucketlists."""
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/bucketlists/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Molo', res.data)

    def test_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        json_data = json.loads(res.data.decode('utf-8').replace("'", "\""))
        res = self.client().get('/bucketlists/{}'.format(json_data['id']))
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Molo', str(res.data))

    def test_invalid_bucketlist_id(self):
        """Test API returns a bad request code for an invalid id."""
        res = self.client().get('/bucketlists/23')
        self.assertEqual(res.status_code, 400)

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist item"""
        res = self.client().post('/bucketlists/', data={'name': 'Dance with a hot girl'})
        self.assertEqual(res.status_code, 201)
        res = self.client().put('/bucketlists/1', \
                    data={'name':"Dance with a hot girl, and her friends."})
        self.assertEqual(res.status_code, 200)
        res = self.client().get('/bucketlists/1')
        self.assertIn(", and her friends.", str(res.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        res = self.client().post('/bucketlists/', data={'name':"Dance with a hot girl."})
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/bucketlists/1')
        self.assertEqual(res.status_code, 200)
        res = self.client().get('/bucketlists/1')
        self.assertEqual(res.status_code, 404)

    def test_bucketlist_delete_bad_id(self):
        """Test that a bad id deletion request yields a 400 error. """
        res = self.client().post('/bucketlists/', data={'name':"Dance with a hot girl."})
        result = self.client().delete('/bucketlists/504')
        self.assertEqual(res.status_code, 400)

    def test_creation_new_item(self):
        """Tests that a user can add an item to a bucket list. (PUT, data)"""
        res = self.client().post('/bucketlists/1/item/', data={'name': ["Dance with a hot girl"]})
        self.assertEqual(res.status_code, 201)

    def test_modifying_bucketlist_item(self):
        """Tests that an item can be modified in a bucketlist."""
        res = self.client().post('/bucketlists/1/item/', data={'name': ["Dance with a hot girl"]})
        res.data = 'and sleep.'
        res = self.client().put('/buckelists/1/item/1', res.data)
        self.assertEqual(res.status_code, 200)
    
    def test_delete_bucketlist_item(self):
        """Tests that an item can be deleted from a bucketlist."""
        res = self.client().post('/bucketlists/1/item/', data={'name': ["Dance with a hot girl"]})
        res = self.client().delete('/bucketlists/1/item/1')
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        """Tears down all test_db data and resets db to empty state"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    flask_testing.main()
