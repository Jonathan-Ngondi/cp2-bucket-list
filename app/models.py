from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask import request, abort
import jwt
import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    user_bucketlists = db.relationship("Bucketlist", backref="users")

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.datetime.now()
       
    
    @staticmethod
    def hash_password(password):
         return generate_password_hash(password)
    
    @staticmethod
    def check_password(hash, password):
        return check_password_hash(hash,password)
    
    def generate_token(data, secret):
        return jwt.encode(data, secret, exp=86400)
    
    def save(self):
        db.session.add(self)
        db.session.commit()


class Bucketlist(db.Model):
    """This class represents the bucketlist table."""

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
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def verify_token(secret):
        token = request.headers.get("Token")
        if token is None:
            abort(401)
        try:
            decoded_data = jwt.decode(token, secret)
        except jwt.ExpiredSignatureError:
            return jsonify({"message":"Your token has expired, please login again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message":"Your token is invalid, use a valid token"}), 401
        return decoded_data
        

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}".format(self.name)

class Items(db.Model):
    
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    bucketlist_id = db.Column(db.Integer, ForeignKey("bucketlists.id_key"))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

