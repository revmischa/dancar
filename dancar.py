from flask import Flask
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import os
from models import db, Device
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
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

@app.route('/devices')
def list_devices():
    devices=Device.query.all()
    return render_template('devices.html', devices=devices)

@app.route('/device/<did>/update', methods=['POST'])
def device_update(did):
    lng = request.form['lng']
    lat = request.form['lat']
    device = Device.query.get(did)
    if not device:
        return "Does not exist"
    device.set_location(lng, lat)
    db.session.commit()
    return "Updated"

@sockets.route('/echo') 
def echo_socket(ws): 
    while True: 
        message = ws.receive() 
        ws.send(message)

if __name__ == '__main__':
    app.run()
