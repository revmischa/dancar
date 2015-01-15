from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from App import DanError, db

def all():
    return User.query.all()
    
def load(uid):
    user = User.query.get(uid)
    if not user : raise DanError(404,"404: Dan not found.")
    return user

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
