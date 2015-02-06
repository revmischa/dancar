#!/usr/bin/env python

import requests

email = "test@test.com"
password = "test"

update = {
    'email': email,
    'password': password
}

print "email is:", email
print "password is:", password
print "endpoint is http://localhost:5000/workspace/api/login'"

s = requests.Session()

s = s.post("http://localhost:5000/workspace/api/login", data=update)

print "Headers the server sent back to us:"
print s.headers

# TODO: next request should use session from previous request
