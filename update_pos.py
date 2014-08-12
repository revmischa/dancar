import requests
import random

lat = -122.25874046835327 + (random.random()-0.5)/100000;
lng = 37.87556521891249 + (random.random()-0.5)/100000;

update = {
	'lat': lat,
	'lng': lng
}
r = requests.post('http://localhost:5000/device/2/update', data=update)
print r.text
