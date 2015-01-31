#!/usr/bin/env python

import requests
import random

email = "test@test.com"
password = "test"

update = {
    'email': email,
    'password': password
}

r = requests.post('http://localhost:5000/workspace/api/login', data=update)
print r.text
