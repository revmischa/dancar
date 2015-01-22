# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from . import app
from .models import User
from flask import render_template as render, jsonify, request
from flask_user import current_user, login_required


@app.route('/')
def index():
    return render('index.html')

@app.route('/user/list')
@login_required
def user_list():
    return render('users.html',users=User.query.all())

@app.route('/user/<uid>')
@login_required
def user_view(uid):
    return render('map.html',user=User.query.get(uid))

@app.route('/user/<uid>/update', methods=['POST'])
@login_required
def user_update(uid):
    user = User.query.get(uid)
    user.set_location(request.form['lng'],request.form['lat'])
    return "Location updated."

@app.route('/api/user/<uid>', methods=['GET'])
@login_required
def api_user(uid):
    user = User.query.get(uid)
    return jsonify({
        'id':uid,
        'name':user.name,
        'updated_location':user.updated_location,
        'lat':user.lat,
        'lng':user.lng
    })


## websocket handler for location push update
# @sockets.route('/echo') 
# def echo_socket(ws): 
#     while True: 
#         message = ws.receive() 
#         ws.send(message)