# Importing this module will bind routes to the app.
# This could be futher split up into submodules if the number of endpoints grows too large for one file.

from dancar import app
from dancar.models import User
from flask import render_template as render, jsonify, request
from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import StringField, SubmitField, validators


## forms

class UserRegisterForm(RegisterForm):
    name = StringField('Name', validators=[
        validators.DataRequired('Name is required')])

class UserEditForm(Form):
    name = StringField('Name', validators=[
        validators.DataRequired('Name is required')])
    submit = SubmitField('Save')


## routes

@app.route('/')
def index():
    return render('index.html')

@app.route('/user/list')
def user_list():
    return render('users.html',users=User.query.all())

@app.route('/user/<uid>')
def user_view(uid):
    return render('map.html',user=User.query.get(uid))

@app.route('/user/<uid>/update', methods=['POST'])
def user_update(uid):
    user = User.query.get(uid)
    user.set_location(request.form['lng'],request.form['lat'])
    return "Location updated."

# @app.route('/user/register')
# def user_register():
#     return render('register.html')

@app.route('/api/user/<uid>', methods=['GET'])
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