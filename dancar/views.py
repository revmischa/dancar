# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from . import app
from .models import db, User
from flask import abort, jsonify, request, session, render_template as render
from flask_user import current_user, login_required
from time import mktime
from flask.ext.login import login_user 

# home
@app.route('/')
def index():
    return render('index.html')

# view all users
@app.route('/user/list')
@login_required
def user_list():
    return render('users.html', users=User.query.all())

# view a user's status
# (should have some security on this)
@app.route('/user/<uid>')
@login_required
def user_view(uid):
    return render('view_user.html', user=User.query.get(uid))

# view myself
@app.route('/user/me')
@login_required
def user_view_me():
    return render('map.view_user', user=current_user)

# update my position
@app.route('/api/user/update', methods=['POST'])
@login_required
def user_update():
    current_user.set_location(request.form['lng'],request.form['lat'])
    if 'location_accuracy_meters' in request.form:
        current_user.location_accuracy_meters = request.form['location_accuracy_meters']
        db.session.commit()
    return "Location updated."

def flatten_user(user):
    if user.updated_location:
        update_unixtime = mktime(user.updated_location.timetuple())
    else:
        update_unixtime = None

    return {
        'id':user.id,
        'name':user.name,
        'updated_location':update_unixtime,
        'lat':user.lat,
        'lng':user.lng,
        'location_accuracy_meters':user.location_accuracy_meters    
    }

# get my user info
@app.route('/api/user/info', methods=['GET'])
def api_user():
    user = current_user
    if not user:
        return jsonify({
            'id': None
        });
    # logged in
    return jsonify(flatten_user(user))

# get positions of all active users
@app.route('/api/user/all', methods=['GET'])
@login_required
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
    email = request.form['email']
    password = request.form['password']
 
    user, user_email = app.user_manager.find_user_by_email(email)

    ok = False

    if user and user.active:
        if app.user_manager.verify_password(password, user) is True:
            user.authenticated = True
            login_user(user, remember=True)
            ok = True

    return jsonify({ 'success': ok })
