from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config


db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    with app.app_context():
         db.create_all()

    return app

