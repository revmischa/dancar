from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from . import db
from flask_user import UserMixin
import datetime
from sqlalchemy import FetchedValue

class GeoReferenced():
    updated_location = db.Column(db.DateTime())
    location_accuracy_meters = db.Column(db.Numeric(asdecimal=False))
    location = db.Column(Geography)

    def set_location(self, lng, lat):
        self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))
        db.session.commit()

    @property
    def lat(self):
        return '0' if self.location is None else str(to_shape(self.location).y)

    @property
    def lng(self):
        return '0' if self.location is None else str(to_shape(self.location).x)

class PickupRequest(db.Model, GeoReferenced):
    __tablename__ = 'pickup_request'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(), server_default=FetchedValue())

    requestor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    driver_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    accepted = db.Column(db.Boolean(), nullable=False, server_default=FetchedValue())
    picked_up = db.Column(db.Boolean(), nullable=False, server_default=FetchedValue())
    completed = db.Column(db.Boolean(), nullable=False, server_default=FetchedValue())
    cancelled = db.Column(db.Boolean(), nullable=False, server_default=FetchedValue())
    use_user_location = db.Column(db.Boolean(), nullable=False, server_default=FetchedValue())

    def confirm(self):
        self.accepted = True
        db.session.commit()

    def cancel(self):
        self.completed = True
        db.session.commit()

    def complete(self):
        self.cancelled = True
        self.completed = True
        db.session.commit()

class UserBase(GeoReferenced):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(), server_default=FetchedValue())

    name = db.Column(db.String())
    email = db.Column(db.String(), nullable=False, unique=True)
    mobile = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default=FetchedValue())
    reset_password_token = db.Column(db.String(), nullable=False, server_default=FetchedValue())
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default=FetchedValue())

    can_pickup = db.Column('can_pickup', db.Boolean(), nullable=False, server_default=FetchedValue())
    has_pickup = db.Column('has_pickup', db.Boolean(), nullable=False, server_default=FetchedValue())
    pickup_enabled = db.Column('pickup_enabled', db.Boolean(), nullable=False, server_default=FetchedValue())
    last_pickup_available_start = db.Column('last_pickup_available_start', db.DateTime(), server_default=FetchedValue())
    last_pickup_available_duration = db.Column('last_pickup_available_duration', db.Interval(), server_default=FetchedValue())

    def __repr__(self):
        return '<user id=%r email=%r>' % (self.id, self.email)

    def enable_pickup(self, duration_secs=0):
        self.last_pickup_available_start = "NOW()"
        delta = datetime.timedelta(0, duration_secs)
        self.last_pickup_available_duration = delta
        self.has_pickup = False
        self.can_pickup = True
        self.pickup_enabled = True
        db.session.commit()

    # requestor requests a pickup from self
    def request_pickup(self, requestor):
        if not self.can_pickup:
            return None
        if not self.pickup_enabled:
            return None

        request = PickupRequest(
            requestor_user_id=requestor.id,
            driver_user_id=self.id,
            location_accuracy_meters=requestor.location_accuracy_meters,
            use_user_location=True,
        )
        request.set_location(requestor.lng, requestor.lat)
        db.session.add(request)
        db.session.commit()
        return request

class User(UserBase, db.Model, UserMixin):
    __tablename__ = 'user'

    pickup_requests = db.relationship('PickupRequest', backref='requestor', foreign_keys=PickupRequest.requestor_user_id, cascade="all,delete")
    pickups = db.relationship('PickupRequest', backref='driver', foreign_keys=PickupRequest.driver_user_id, cascade="all,delete")

class AvailableDancars(UserBase, db.Model, UserMixin):
    __tablename__ = 'available_dancars'
    def __repr__(self):
        return '<dancars u=%r>' % self.id
