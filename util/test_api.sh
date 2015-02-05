#!/usr/bin/env python

import requests

email = "test@test.com"
password = "test"

endpoint='http://localhost:5000/workspace/api/login'
update = {
    'email': email,
    'password': password
}

print "email is:", email
print "password is:", password
print "endpoint is:", endpoint

r = requests.post(endpoint, data=update)
print r.text
