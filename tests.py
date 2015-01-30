import os
import dancar
import unittest
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

    def test_login_logout_web(self):
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


if __name__ == '__main__':
    unittest.main()
