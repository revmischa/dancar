from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import os
from models import db, User
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
))

def get_db():
    if not hasattr(g, 'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'pg_db'):
        g.pg_db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/list')
def user_list():
    users=User.query.all()
    return render_template('users.html', users=users)

@app.route('/user/<uid>')
def user_view(uid):
    user = User.query.get(uid)
    if not user:
        abort(404)
    return render_template('map.html', user=user)

@app.route('/user/<uid>/update', methods=['POST'])
def user_update(uid):
    lng = request.form['lng']
    lat = request.form['lat']
    user = User.query.get(uid)
    if not user:
        return "Does not exist"
    user.set_location(lng, lat)
    db.session.commit()
    return "Updated"

@app.route('/api/user/<uid>', methods=['GET'])
def api_user(uid):
    user = User.query.get(uid)
    if not user:
        return "Does not exist"
    ret = dict(id=uid, name=user.name, updated_location=user.updated_location)
    if user.location:
        ret.lat = user.get_lat();
        ret.lng = user.get_lng();
    return jsonify(**ret)


@sockets.route('/echo') 
def echo_socket(ws): 
    while True: 
        message = ws.receive() 
        ws.send(message)

if __name__ == '__main__':
    app.run()
