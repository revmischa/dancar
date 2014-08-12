from dancar import db
from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geography

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
