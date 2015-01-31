#!/usr/bin/env python

import json
import os
import pprint
import random
import sys
from bs4 import BeautifulSoup

sys.path.append("..")
import dancar

app = dancar.app.test_client()
dancar.app.config['CSRF_ENABLED'] = False

def login_web(username, password):
    form = app.get('/user/sign-in').data
    soup = BeautifulSoup(form)
    token = soup.find(id='csrf_token').get('value')

    return app.post('/user/sign-in', data=dict(
        csrf_token=token,
        email=username,
        password=password
    ), follow_redirects=True)

rv = login_web('test@test.com', 'test')
lng = -122.25874046835327 + (random.random()-0.5)/1000
lat = 37.87556521891249 + (random.random()-0.5)/1000
rv = app.post('/api/user/update', data=dict(lng=lng, lat=lat))
rv = app.get('/api/user/info')
ret = json.loads(rv.data)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(ret)
