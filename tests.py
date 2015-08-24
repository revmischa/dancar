import os
import dancar
import unittest
import random
import json
from dancar.models import User, AvailableDancars
from bs4 import BeautifulSoup

class WebTestCase(unittest.TestCase):
    def setUp(self):
        self.app = dancar.app.test_client()
        self.db = dancar.db
        dancar.app.config['CSRF_ENABLED'] = False
        # if self.app.config['TESTING']:
        #     print "Creating database"


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

    # request a ride
    def test_pickup_request(self):
        db = self.db
        rv = self.login_web('test@test.com', 'test')

        # create driver user
        driver_user = self.create_test_user('testdriver')
        driver_user.enable_pickup(duration_secs=2)

        # list available drivers
        dancars = AvailableDancars.query.all()
        assert len(dancars) == 1, "Found dancar driver for pickup"

        db.session.delete(driver_user)
        db.session.commit()

    def login_api(self, email, password):
        endpoint = '/api/login'
        req = {
            'email': email,
            'password': password
        }
        r = self.app.post(endpoint, data=req)
        res = json.loads(r.data)
        return res['success']

    def create_test_user(self, name):
        u = User()
        u.name = name
        u.email = name + '@test.com'
        u.password = 'x'
        u.reset_password_token = 'x'
        self.db.session.add(u)
        self.db.session.commit()

        lng = -122.25874046835327 + (random.random()-0.5)/100
        lat = 37.87556521891249 + (random.random()-0.5)/100
        u.set_location(lng, lat)

        return u        

    def test_api_login(self):
        assert self.login_api('test@test.com', 'test') is True, 'Logged in via API'
        assert self.login_api('test@test.com', 'not') is False, 'Failed login via API with invalid password'

if __name__ == '__main__':
    unittest.main()
