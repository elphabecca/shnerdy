from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_to_db(app):
    """Connect to db"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///TBD' # <-- CREATE A DB!!!
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

connect_to_db(app)