
# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from App import app,db
from Model import User
from flask import render_template as render, jsonify, request

# @sockets.route('/echo') 
# def echo_socket(ws): 
#     while True: 
#         message = ws.receive() 
#         ws.send(message)


@app.route('/')
def index():
    return render('index.html')

@app.route('/user/list')
def user_list():
    return render('users.html',users=User.all())

@app.route('/user/<uid>')
def user_view(uid):
    return render('map.html',user=User.load(uid))

@app.route('/user/<uid>/update', methods=['POST'])
def user_update(uid):
    user = User.load(uid)
    user.set_location(request.form['lng'],request.form['lat'])
    db.session.commit()
    return "Location updated."

@app.route('/api/user/<uid>', methods=['GET'])
def api_user(uid):
    user = User.load(uid)
    return jsonify({
        'id':uid,
        'name':user.name,
        'updated_location':user.updated_location,
        'lat':user.lat,
        'lng':user.lng
    })
