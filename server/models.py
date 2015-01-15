from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from dancar import db

class User(db.Model):

    # DB Setup
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

    @property
    def lng (self) :
        return 0 if self.location is None else to_shape(self.location).x

    @property
    def lat(self):
        return 0 if self.location is None else to_shape(self.location).y
