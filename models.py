from flask.ext.sqlalchemy import SQLAlchemy
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_X, ST_Y
from geoalchemy2.shape import to_shape
from sqlalchemy.ext.declarative import declarative_base
from dancar import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    updated_location = db.Column(db.DateTime())
    location = db.Column(Geography)

    def __init__(self, name, location):
        self.name = name
        self.location = location

    def __repr__(self):
        return '<user id=%r>' % self.id

    def set_location(self, lng, lat):
        self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))

    def get_lng(self):
        point = to_shape(self.location)
        return point.x
    def get_lat(self):
        point = to_shape(self.location)
        return point.y
        