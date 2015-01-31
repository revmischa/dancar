#!/bin/bash

# crude way of updating the test user's location
#
# The location gets updated twice because current location
# does not get updated unless there is a new location
#
# I did this in bash for now because I was unable to figure
# out how to use the requests module to POST a json
# array in such a way that Flask would accept it.

email="test@test.com"
password="test"

lat=38.8784970629
lng=-122.26222

COMMAND=$(cat <<EOF
curl -i -H "Content-Type: application/json" -X POST -d \
'{"lat": ${lat}, "lng": ${lng}, "password": "${password}", "email": "${email}"}' \
http://localhost:5000/workspace/api/update
EOF
)

eval ${COMMAND}

echo
echo

lat=38.1784970629 
lng=-122.36222

eval ${COMMAND}
echo
