from sqlalchemy import FetchedValue, Column, DateTime, Numeric, Integer, Boolean, String, ForeignKey, Interval
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_AsGeoJSON
import sqlalchemy.types as types
from flask_user import UserMixin
from dancar import db
import datetime
import json

class PointGeography(types.UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def column_expression(self, col):
        return ST_AsGeoJSON(col, type_=self)

class GeoReferenced():
    updated_location = Column(DateTime())
    location_accuracy_meters = Column(Numeric(asdecimal=False))
    location = Column(PointGeography)

    def set_location(self, lng, lat):
        if lat is None or lng is None:
            self.location = None
        else:
            self.location = "POINT(%0.16f %0.16f)" % (float(lng), float(lat))
        db.session.commit()

    @property
    def lat(self):
        if self.location is None:
            return None 
        return parse_point(self.location)[1]
        # return None if self.location is None else str(to_shape(self.location).y)

    @property
    def lng(self):
        if self.location is None:
            return None 
        return parse_point(self.location)[0]
        # return None if self.location is None else str(to_shape(self.location).x)

def parse_point(point):
    geo = json.loads(point)
    return geo['coordinates']

    @classmethod
    def within_clause(cls, latitude, longitude, distance):
        """Return a within clause that explicitly casts the `latitude` and 
          `longitude` provided to geography type.
        """
        
        attr = '%s.location' % cls.__tablename__
        
        point = 'POINT(%0.8f %0.8f)' % (longitude, latitude)
        location = "ST_GeographyFromText(E'SRID=4326;%s')" % point
        
        return 'ST_DWithin(%s, %s, %d)' % (attr, location, distance)

class PickupBase(GeoReferenced):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(), server_default=FetchedValue())
    accepted = Column(Boolean(), nullable=False, server_default=FetchedValue())
    picked_up = Column(Boolean(), nullable=False, server_default=FetchedValue())
    completed = Column(Boolean(), nullable=False, server_default=FetchedValue())
    cancelled = Column(Boolean(), nullable=False, server_default=FetchedValue())
    use_user_location = Column(Boolean(), nullable=False, server_default=FetchedValue())

    def confirm(self):
        self.accepted = True
        self.completed = False
        db.session.commit()

    def cancel(self):
        self.completed = True
        self.cancelled = True
        db.session.commit()

    def pickup(self):
        self.picked_up = True
        self.completed = False
        db.session.commit()

    def complete(self):
        self.completed = True
        db.session.commit()

class PickupRequest(PickupBase, db.Model):
    __tablename__ = 'pickup_request'
    requestor_user_id = Column(Integer, ForeignKey('user.id'))
    driver_user_id = Column(Integer, ForeignKey('user.id'))

class AvailblePickupRequests(PickupBase, db.Model):
    __tablename__ = 'available_pickup_requests'
    requestor_user_id = Column(Integer, ForeignKey('user.id'))
    driver_user_id = Column(Integer, ForeignKey('user.id'))

class UserBase(GeoReferenced):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(), server_default=FetchedValue())

    name = Column(String())
    email = Column(String(), nullable=False, unique=True)
    mobile = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False, server_default=FetchedValue())
    reset_password_token = Column(String(), nullable=False, server_default=FetchedValue())
    active = Column('is_active', Boolean(), nullable=False, server_default=FetchedValue())

    can_pickup = Column('can_pickup', Boolean(), nullable=False, server_default=FetchedValue())
    has_pickup = Column('has_pickup', Boolean(), nullable=False, server_default=FetchedValue())
    pickup_enabled = Column('pickup_enabled', Boolean(), nullable=False, server_default=FetchedValue())
    last_pickup_available_start = Column('last_pickup_available_start', DateTime(), server_default=FetchedValue())
    last_pickup_available_duration = Column('last_pickup_available_duration', Interval(), server_default=FetchedValue())

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
