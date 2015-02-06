# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from . import app
from .models import User
from flask import abort, jsonify, request, session, render_template as render
from flask_user import current_user, login_required

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
    return render('map.html',user=User.query.get(uid))

# view myself
@app.route('/user/me')
@login_required
def user_view_me():
    return render('map.html',user=current_user)

# update my position
@app.route('/api/user/update', methods=['POST'])
@login_required
def user_update():
    current_user.set_location(request.form['lng'],request.form['lat'])
    return "Location updated."

# get my user info
@app.route('/api/user/info', methods=['GET'])
@login_required
def api_user():
    user = current_user
    return jsonify({
        'id':user.id,
        'name':user.name,
        'updated_location':user.updated_location,
        'lat':user.lat,
        'lng':user.lng
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
