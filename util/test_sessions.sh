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

sesh = requests.Session()

res = sesh.post("http://localhost:5000/workspace/api/login", data=update)

print "Headers the server sent back to us:"
print res.headers

res = sesh.get("http://localhost:5000/api/user/info")
print res.content