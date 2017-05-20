from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from instance.config import APP_CONFIG
from flask_bcrypt import Bcrypt

DB = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG[config_name])

    return Bcrypt(app)

