from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from dancar import error, db
from flask_user import UserMixin

class User(db.Model, UserMixin):
    # DB Setup
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    updated_location = db.Column(db.DateTime())
    location = db.Column(Geography)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(), nullable=False, server_default='')
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    def __init__(self, name, location):
        self.name = name
        self.location = location

    def __repr__(self):
        return '<user id=%r>' % self.id

    def set_location(self, lng, lat):
        self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))
        db.session.commit()

    @property
    def lng (self) :
        return 0 if self.location is None else to_shape(self.location).x

    @property
    def lat(self):
        return 0 if self.location is None else to_shape(self.location).y
