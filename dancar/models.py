from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from . import error, db
from flask_user import UserMixin
import datetime

class UserBase():
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    updated_location = db.Column(db.DateTime())
    location_accuracy_meters = db.Column(db.Numeric(asdecimal=False))
    location = db.Column(Geography)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(), nullable=False, server_default='')
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    can_pickup = db.Column('can_pickup', db.Boolean(), nullable=False, server_default='1')
    has_pickup = db.Column('has_pickup', db.Boolean(), nullable=False, server_default='1')
    pickup_enabled = db.Column('pickup_enabled', db.Boolean(), nullable=False, server_default='0')
    last_pickup_available_start = db.Column('last_pickup_available_start', db.DateTime())
    last_pickup_available_duration = db.Column('last_pickup_available_duration', db.Interval())

    def __repr__(self):
        return '<user id=%r>' % self.id

    def enable_pickup(self, duration_secs=0):
        self.last_pickup_available_start = "NOW()"
        delta = datetime.timedelta(0, duration_secs)
        self.last_pickup_available_duration = delta
        self.has_pickup = False
        self.can_pickup = True
        self.pickup_enabled = True
        db.session.commit()

    def set_location(self, lng, lat):
        self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))
        db.session.commit()

    @property
    def lat(self):
        return 0 if self.location is None else to_shape(self.location).y

    @property
    def lng(self):
        return 0 if self.location is None else to_shape(self.location).x


class User(UserBase, db.Model, UserMixin):
    __tablename__ = 'user'

class AvailableDancars(UserBase, db.Model, UserMixin):
    __tablename__ = 'available_dancars'
    def __repr__(self):
        return '<dancars u=%r>' % self.id
