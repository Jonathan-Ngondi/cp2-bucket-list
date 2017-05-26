from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask import request, abort, jsonify
import jwt
import datetime


class User(db.Model):
    """Class for creating Bucketlist schema,as well as CRUD methods, as well as static methods
       for user validation, as well as user verification.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(255))
    email = db.Column(db.String(50))
    user_bucketlists = db.relationship("Bucketlist", backref="users")

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.datetime.now()    

    @staticmethod
    def hash_password(password):
        """This method hashes a user password."""
        return generate_password_hash(password)

    @staticmethod
    def check_password(hash, password):
        """Checks and verifies the password of a user login."""
        return check_password_hash(hash,password)
    
    @staticmethod
    def generate_token(self, data, secret):
        """Generates a token for user session."""
        return jwt.encode(data, secret, exp=86400)

    @staticmethod
    def verify_token(secret):
        """Verifies the token passed in the header."""
        token = request.headers.get("token")
        if token is None:
            abort(401)
        try:
            decoded_data = jwt.decode(token, secret)
        except:
            return "Your token has expired, please login again."
        
        return decoded_data

    def save(self):
        """Saves data to database."""
        db.session.add(self)
        db.session.commit()


class Bucketlist(db.Model):
    """Class for creating Bucketlist schema,as well as CRUD methods, as well as some query
       methods.
    """

    __tablename__ = 'bucketlists'

    id_key = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    created_by = db.Column(db.Integer, ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    user = db.relationship("User", back_populates="user_bucketlists")

    def __init__(self, name, created_by):
        """Initialize tables with name"""
        self.name = name
        self.created_by = created_by

    def save(self):
        """Saves bucketlist data to database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    


    def __repr__(self):
        return "<Bucketlist: {}".format(self.name)

class Items(db.Model):
    """Class for creating Items schema in database as well as methods for CRUD operations."""

    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    bucketlist_id = db.Column(db.Integer, ForeignKey("bucketlists.id_key"))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def __init__(self, name, bucketlist_id):
        self.name = name
        self.bucketlist_id = bucketlist_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

