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
* Android client
* iOS client
* Web client
* WebSocket push event support, falling back to poll-based location update
* ~~Poll-based location updating~~ done
* Notification system to inform users of Dancar status, and inform Dancar driver of pickup requests
* Cooler interface
* Cooler map markers

## Running the Server
* Install postgresql, postGIS
```
createdb dancar

#(might need to do this if not using Postgres.app): 
echo "CREATE EXTENSION postgis" | psql -U postgres dancar

psql dancar < schema.txt
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python runserver.py
```
And you should be good to go.

## Try it out
View the DanH user map, then run `python util/update_pos.py` to update the DanCar with random coordinates.

