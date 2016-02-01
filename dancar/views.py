# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from dancar import app
from .models import db, User, AvailableDancars, PickupRequest, AvailblePickupRequests
from flask import abort, jsonify, request, session, redirect, render_template as render
from flask_user import current_user, login_required
from time import mktime
from flask.ext.login import login_user 
from functools import wraps

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None or not current_user.is_authenticated or current_user.is_anonymous:
            return jsonify({'needs_login': True}), 401
        return f(*args, **kwargs)
    return decorated_function

# home
@app.route('/')
def index():
    return redirect('/static/index.html')

# update my position
@app.route('/api/user/update', methods=['POST'])
@api_login_required
def user_update():
    current_user.set_location(request.values['lng'],request.values['lat'])
    if 'location_accuracy_meters' in request.values:
        current_user.location_accuracy_meters = request.values['location_accuracy_meters']
        db.session.commit()
    return "Location updated."

# get my user info
@app.route('/api/user/info', methods=['GET'])
@api_login_required
def api_user():
    return jsonify(flatten_user(current_user))

# get positions of all active users
@app.route('/api/user/all', methods=['GET'])
@api_login_required
def api_all_users():
    ret = []

    # users = User.query.filter_by(is_active=1).all();
    users = User.query.all();

    for user in users:
        if user.updated_location:
            update_unixtime = mktime(user.updated_location.timetuple())
        else:
            update_unixtime = None

        ret.append(flatten_user(user))

    return jsonify({
        'users': ret
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.values['email']
    password = request.values['password']
 
    user, user_email = app.user_manager.find_user_by_email(email)

    ok = False

    if user and user.active:
        if app.user_manager.verify_password(password, user) is True:
            user.authenticated = True
            login_user(user, remember=True)
            ok = True

    return jsonify({ 'success': ok })

# get dancars available for picking up passengers
@app.route('/api/car/available', methods=['GET'])
@api_login_required
def api_available_cars():
    cars = AvailableDancars.query.all()
    ret = [flatten_user(car) for car in cars]
    return jsonify({ 'cars': ret })

# request a pickup
# should pass in lng/lat/location_accuracy_meters (will use current_user's by default)
@app.route('/api/car/request_pickup/<car_id>', methods=['POST'])
@api_login_required
def api_request_pickup(car_id):
    # sanity-check that this car is still available
    car = AvailableDancars.query.filter(AvailableDancars.id == car_id).scalar()
    if not car:
        return jsonify({ 'message': 'This car is not available for pickup' })

    # request pickup
    pickup_request = car.request_pickup(current_user)
    if not pickup_request:
        return jsonify({ 'message': 'Pickup request failed' })

    # specific lng/lat?
    if 'lng' in request.values and 'lat' in request.values:
        pickup_request.set_location(request.values['lng'], request.values['lat'])
        pickup_request.use_user_location = False
        pickup_request.location_accuracy_meters = None
        db.session.commit()

    return jsonify({ 'message': 'Pickup requested', 'pickup': flatten_pickup_request(pickup_request) })


#### PICKUPS

# confirm
@app.route('/api/pickup/<pickup_id>/confirm', methods=['POST'])
@api_login_required
def api_confirm_pickup(pickup_id):
    # check view to make sure this is still available 
    if not AvailblePickupRequests.query.filter(AvailblePickupRequests.id == pickup_id).scalar():
        return jsonify({ 'message': 'Failed to confirm pickup' })
    # confirm it
    pickup = PickupRequest.query.filter(PickupRequest.id == pickup_id).scalar()
    pickup.confirm()
    return jsonify({ 'message': 'Pickup confirmed', 'pickup': flatten_pickup_request(pickup) })

# cancel
@app.route('/api/pickup/<pickup_id>/cancel', methods=['POST'])
@api_login_required
def api_cancel_pickup(pickup_id):
    pickup = PickupRequest.query.filter(PickupRequest.id == pickup_id).scalar()
    if not pickup:
        return jsonify({ 'message': 'Failed to cancel pickup' })
    pickup.cancel()
    return jsonify({ 'message': 'Pickup cancelled', 'pickup': flatten_pickup_request(pickup) })

# picked up
@app.route('/api/pickup/<pickup_id>/picked_up', methods=['POST'])
@api_login_required
def api_picked_up_pickup(pickup_id):
    pickup = PickupRequest.query.filter(PickupRequest.id == pickup_id).scalar()
    if not pickup:
        return jsonify({ 'message': 'Failed to register pickup' })
    pickup.pickup()
    return jsonify({ 'message': 'Now on your way', 'pickup': flatten_pickup_request(pickup) })

# complete
@app.route('/api/pickup/<pickup_id>/complete', methods=['POST'])
@api_login_required
def api_complete_pickup(pickup_id):
    pickup = PickupRequest.query.filter(PickupRequest.id == pickup_id).scalar()
    if not pickup:
        return jsonify({ 'message': 'Failed to complete pickup' })
    pickup.complete()
    return jsonify({ 'message': 'Pickup completed', 'pickup': flatten_pickup_request(pickup) })


#####

def flatten_pickup_request(req):
    if req.updated_location:
        update_unixtime = mktime(req.updated_location.timetuple())
    else:
        update_unixtime = None

    lng = req.lng
    lat = req.lat
    location_accuracy_meters = req.location_accuracy_meters

    if req.use_user_location:
        # override with user's current location?
        u = req.requestor
        lng = u.lng
        lat = u.lat
        location_accuracy_meters = u.location_accuracy_meters

    return {
        'id':req.id,
        'created':req.created,
        'updated_location':update_unixtime,
        'lat':lat,
        'lng':lng,
        'location_accuracy_meters':location_accuracy_meters, 
        'accepted':req.accepted,
        'picked_up':req.picked_up,
        'completed':req.completed,
        'cancelled':req.cancelled,
        'use_user_location':req.use_user_location,
        'requestor_name':req.requestor.name,
        'requestor_email':req.requestor.email,
        'requestor_mobile':req.requestor.mobile,
        'driver_name':req.driver.name,
        'driver_email':req.driver.email,
        'driver_mobile':req.driver.mobile,
    }

def flatten_user(user):
    if user.updated_location:
        update_unixtime = mktime(user.updated_location.timetuple())
    else:
        update_unixtime = None

    return {
        'id':user.id,
        'email':user.email,
        'mobile':user.mobile,
        'name':user.name,
        'updated_location':update_unixtime,
        'lat':user.lat,
        'lng':user.lng,
        'location_accuracy_meters':user.location_accuracy_meters,   
    }
