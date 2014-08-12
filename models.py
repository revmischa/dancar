from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from geoalchemy2 import Geography
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/dancar'
db = SQLAlchemy(app)

class Device(db.Model):
    __tablename__ = 'device'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    location = db.Column(Geography)

    def __init__(self, name, location):
        self.name = name
        self.location = location

    def __repr__(self):
        return '<id %r>' % self.id

    def set_location(self, lng, lat):
        self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))
