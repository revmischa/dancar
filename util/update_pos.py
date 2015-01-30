#!/usr/bin/env python

import requests
import random

# log in
r = requests.post('http://localhost:5000/user/sign-in', data={'email':'test@test.com', 'password':'test'})
print r.text

lng = -122.25874046835327 + (random.random()-0.5)/100
lat = 37.87556521891249 + (random.random()-0.5)/100

update = {
    'lat': lat,
    'lng': lng
}
r = requests.post('http://localhost:5000/user/1/update', data=update)
#print r.text
