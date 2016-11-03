from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# MODEL DEFINITIONS

class User(db.Model):
    """Class for users of Shnerdy."""

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(50),
                           nullable=False)
    username = db.Column(db.String(50),
                         nullable=False,
                         unique=True)
    password = db.Column(db.String(50),
                         nullable=False)
    oauth = db.Column(db.String(100),
                      unique=True)

    def __repr__(self):
        """Show info about the user."""

        return "<id=%s first_name=%s username=%s>" % (
                self.id, self.first_name, self.username)

    # Relationships
    terms = db.relationship('Term', backref='user')

class Term(db.Model):
    """Class for user-created categories and terms of Shnerdy searches."""

    __tablename__ = 'terms'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    term = db.Column(db.String(75),
                     nullable=False)
    parent_id = db.Column(db.Integer,
                          db.ForeignKey('terms.id'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    def __repr__(self):
        """Show info about the term."""

        return "<id=%s term=%s parent_id=%s user_id=%s>" % (
                self.id, self.term, self.parent_id, self.user_id)


def connect_to_db(app):
    """Connect to db"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///shnerdy'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    print "This is in the model file -- you're in the DB"



# For when you forget later but you had to dump and re-do your db:
# db.create_all()

