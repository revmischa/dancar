# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from . import app
from .models import User
from flask import abort, jsonify, request
from flask_user import current_user, login_required

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

# login via api
@app.route('/workspace/api/login', methods=['POST'])
def workspace_api_login():
    email = request.form['email']
    password = request.form['password']

    # value for email gets passed.  this isnt matching
    # in user_manager properly for it though
    if app.user_manager.find_user_by_email(email) is True:
        pass
    else:
        return("Email Not Found"), 422

## websocket handler for location push update
# @sockets.route('/echo') 
# def echo_socket(ws): 
#     while True: 
#         message = ws.receive() 
#         ws.send(message)
