import os
import dancar
import unittest
import random
import json
from bs4 import BeautifulSoup

class WebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = dancar.app.test_client()
        dancar.app.config['CSRF_ENABLED'] = False

    def login_web(self, username, password):
        # get CSRF token
        form = self.app.get('/user/sign-in').data
        soup = BeautifulSoup(form)
        token = soup.find(id='csrf_token').get('value')

        return self.app.post('/user/sign-in', data=dict(
            csrf_token=token,
            email=username,
            password=password
        ), follow_redirects=True)

    def logout_web(self):
        return self.app.get('/user/sign-out', follow_redirects=True)

    def test_web_login_logout(self):
        # login
        rv = self.login_web('test@test.com', 'test')
        assert 'You have signed in successfully' in rv.data
        # logout
        rv = self.logout_web()
        assert 'You have signed out successfully' in rv.data
        # invalid username
        rv = self.login_web('bogus', 'default')
        assert 'Invalid Email' in rv.data
        # invalid password
        rv = self.login_web('test@test.com', 'defaultx')
        assert 'Incorrect Email and Password' in rv.data

    def test_api_location_client(self):
        # test logging in and updating and retrieving the user's position
        rv = self.login_web('test@test.com', 'test')
        assert 'You have signed in successfully' in rv.data
        # update position
        lng = -122.25874046835327 + (random.random()-0.5)/100
        lat = 37.87556521891249 + (random.random()-0.5)/100
        rv = self.app.post('/api/user/update', data=dict(lng=lng, lat=lat))
        assert 'Location updated' in rv.data
        # get position
        rv = self.app.get('/api/user/info')
        ret = json.loads(rv.data)
        assert str(ret.get('lat')) == str(lat), 'Got updated lat'
        assert str(ret.get('lng')) == str(lng), 'Got updated lng'


if __name__ == '__main__':
    unittest.main()
