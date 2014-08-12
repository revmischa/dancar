from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import os

app = Flask(__name__)
app.config.update(dict(
    DATABASE="postgresql://localhost/dancar",
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('DANCAR_SETTINGS', silent=True)

db = SQLAlchemy(app)

engine = create_engine(app.config.get('DATABASE'), echo=True)
Session = sessionmaker(bind=engine)

# from models import Device

def connect_db():
    return Session()

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
    db = get_db()
    cur = db.execute('select id,name,location from device order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', devices=devices)

if __name__ == '__main__':
    app.run()
