import os
import dancar
import unittest
import random
import json
from dancar.models import User, AvailableDancars, PickupRequest, AvailblePickupRequests
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
        soup = BeautifulSoup(form, "html.parser")
        token = soup.find(id='csrf_token').get('value')

        return self.app.post('/user/sign-in', data=dict(
            csrf_token=token,
            email=username,
            password=password
        ), follow_redirects=True)

    def logout_web(self):
        return self.app.get('/user/sign-out', follow_redirects=True)

    def test_api_location_client(self):
        # test logging in and updating and retrieving the user's position
        rv = self.login_web('test@test.com', 'test')
        # update position
        lng, lat = self.random_lng_lat()
        rv = self.app.post('/api/user/update', data=dict(lng=lng, lat=lat))
        self.assertIn('Location updated', rv.data, "Did not get location update message after /api/user/update")
        # get position
        rv = self.app.get('/api/user/info')
        ret = json.loads(rv.data)
        self.assertEquals(str(ret.get('lat')), str(lat), 'Updated lat value did not save. Got %s expected %s' % (ret.get('lat'), lat))
        self.assertEquals(str(ret.get('lng')), str(lng), 'Updated lng value did not save')

    # request a ride
    def test_pickup_request(self):
        db = self.db
        rv = self.login_web('test@test.com', 'test')

        # create driver user
        driver_user = self.create_test_user('testdriver')
        driver_user.enable_pickup(duration_secs=5)

        # list available drivers
        dancars = AvailableDancars.query.all()
        self.assertEquals(len(dancars), 1, "Did not find expected number of dancar drivers for pickup")
        car = dancars[0]

        # request a pickup
        lng, lat = self.random_lng_lat()
        rv = self.app.post('/api/car/request_pickup/' + str(car.id), data=dict(lng=lng, lat=lat))
        self.assertEquals(rv.status_code, 200, "Did not get OK status from pickup request API")
        pickup = json.loads(rv.data)['pickup']
        self.assertFalse(pickup['use_user_location'], "Failed to specify manually-defined pickup location")
        self.assertEquals(str(pickup['lng']), str(lng), "Did not use manually-defined pickup location")
        self.assertEquals(str(pickup['lat']), str(lat), "Did not use manually-defined pickup location")
        self.assertEquals(pickup['requestor_email'], 'test@test.com', "Got incorrect pickup requestor email")
        self.assertEquals(pickup['driver_email'], driver_user.email, "Got incorrect pickup driver email")

        # confirm the pickup. should still be available
        available_pickups = AvailblePickupRequests.query.all()
        self.assertEquals(len(available_pickups), 1, "Did not find available pickup request")
        rv = self.app.post('/api/pickup/' + str(pickup['id']) + '/confirm')
        res = json.loads(rv.data)
        self.assertEquals(res['message'], 'Pickup confirmed', "Did not get confirmed pickup message")
        # dancar should still be available
        dancars = AvailableDancars.query.all()
        self.assertEquals(len(dancars), 1, "Did not find dancar driver for pickup")
        # pickup request should be no longer available
        available_pickups = AvailblePickupRequests.query.all()
        self.assertEquals(len(available_pickups), 0, "Still found pickup request after confirming")

        PickupRequest.query.delete()
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
        u.mobile = '+1 555 555-6655'
        self.db.session.add(u)
        self.db.session.commit()

        lng, lat = self.random_lng_lat()
        u.set_location(lng, lat)

        return u        

    def test_api_login(self):
        self.assertTrue(self.login_api('test@test.com', 'test'), 'Failed to log in via API')
        self.assertFalse(self.login_api('test@test.com', 'not'), 'Did not fail login via API with invalid password')

    def random_lng_lat(self):
        lng = -122.25874046835327 + (random.random()-0.5)/100
        lat = 37.87556521891249 + (random.random()-0.5)/100
        return lng, lat

if __name__ == '__main__':
    unittest.main()
