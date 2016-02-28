![Build status](https://travis-ci.org/revmischa/dancar.svg?branch=master)

# DANCAR
## "The Uber of DanH"

```
 _____________________ 
 ==========| ======|=\\
           |  ó ò  |  \\         o
           |   c   |   \\        |
           |  ===  |___..\_      |
           |=======       |=``----._
           |==           _|          )
           |            /..--..      |
           |           //. - . \  == )
            \ _______// .     . \    |
   ssssss             | .  O  . |____\
 =====================   .   .
                           `
```

## Problem
* DanH has my car, we need to be able to summon him for rides when drunk.
* DanH needs to know our location
* We need to know DanH's location

## Approach
* Track users via smartphone apps. Simple read of GPS position, HTTP POST to update current location.
* Display users and Dancar in real-time using Google Maps API and PostGIS.
* Magic happens in user.location update trigger, see [`schema.sql`](schema.sql)

## Tasks:
* Cordova/PhoneGap interface
* ~~Poll-based location updating~~ done
* ~~User registration / login with Flask-User~~ done
* Notification system to inform users of Dancar status, and inform Dancar driver of pickup requests
* Cooler map markers

## Frontend/mobile app development:
(You need node.js)
In `ui/` directory
```
cd ui
npm install
gulp  # serves up local app

# (optional) pick a platform to develop on
ionic platform add android
ionic platform add ios
ionic platform add osx

# run local dev server
gulp
ionic serve osx
```


## Running the backend server

* Step 1: Install PostgreSQL, postGIS

### (LINUX)
```
sudo -u postgres -- createuser -s $USER
createdb dancar
```

### (OSX)
Install [postgres.app](http://postgresapp.com/)
```
echo "export PATH=/Applications/Postgres.app/Contents/Versions/9.5/bin/:$PATH" >> ~/.profile
echo "export PGHOST=localhost" >> ~/.profile
```
Reopen your terminal

### Init database
```
createdb dancar
echo "CREATE EXTENSION postgis" | psql dancar
make init-schema
```

### Grab python modules
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python runserver.py
```
 
And you should be good to go. 
 
## Try it out
`make server`   
`make test`   
View the DanH user map, then run `python util/update_pos.py` to update the DanCar with random coordinates.
