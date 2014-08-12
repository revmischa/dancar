from flask import Flask
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import os
from models import db, Device

app = Flask(__name__)
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
def show_entries():
    devices=Device.query.all()
    return render_template('show_entries.html', devices=devices)

if __name__ == '__main__':
    app.run()
