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
    email = db.Column(db.String(75),
                      nullable=False,
                      unique=True)
    username = db.Column(db.String(50),
                         unique=True)
    password = db.Column(db.String(50))
    oauth_id = db.Column(db.String(50),
                         unique=True)

    def __repr__(self):
        """Show info about the user."""

        return "<id=%s first_name=%s username=%s>" % (
                self.id, self.first_name, self.username)

    # Relationships
    terms = db.relationship('Term', backref='user')
    ratings = db.relationship('Rating', backref='user')
    shirts = db.relationship('Shirt', backref='user')


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


class Rating(db.Model):
    """Class for yay or nay ratings that the user gives to a shirt."""

    __tablename__ = 'ratings'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    etsy_id = db.Column(db.String(25),
                         nullable=False,
                         unique=True)
    rating = db.Column(db.Boolean,
                       nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    def __repr__(self):
        """Show info about the rating."""

        return "<id=%s etsy_id=%s rating=%s user_id=%s>" % (
                self.id, self.etsy_id, self.rating, self.user_id)

    # Relationships
    shirts = db.relationship('Shirt', backref='rating')

class Shirt(db.Model):
    """Class to hold shirt data"""

    __tablename__ = 'shirts'

    id = db.Column(db.String(25),
                   db.ForeignKey('ratings.etsy_id'),
                   primary_key=True,
                   nullable=False)
    price = db.Column(db.String(10),
                         nullable=False)
    img = db.Column(db.String(150),
                         nullable=False)
    url = db.Column(db.String(150),
                         nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    def __repr__(self):
        """Show info about the shirt."""

        return "<id=%s price=%s img=%s url=%s>" % (
                self.id, self.price, self.img, self.url)


# EXAMPLE DATA FOR TESTING:
def example_data():
    """Create example data for testing purposes"""

    phoebe = User(first_name='Phoebe', email='phoebe@gmail.com', username='smellycat', password='smellycat')
    monica = User(first_name='Monica', email='monica@gmail.com', username='puffyhair', password='puffyhair')
    rachel = User(first_name='Rachel', email='rachel@gmail.com', username='igotofftheplane', password='igotofftheplane')
    joey = User(first_name='Joey', email='joey@gmail.com', username='hey', password='hey')
    chandler = User(first_name='Chandler', email='chandler@gmail.com', username='thanksgiving', password='thanksgiving')
    ross = User(first_name='Ross', email='ross@gmail.com', username='iloverachel', password='iloverachel')


    star_trek = Term(term='Star Trek', user=ross)
    shut_up_wesley = Term(term="Shut Up Wesley", parent_id=star_trek.id, user=ross)
    make_it_so = Term(term="Make it so", parent_id=star_trek.id, user=ross)
    smellycats = Term(term='Smelly Cat', user=phoebe)
    grumpycat = Term(term="Grumpy Cat", parent_id=smellycats.id, user=phoebe)
    music = Term(term="Music", user=phoebe)
    guitar = Term(term="Guitar", parent_id=music.id, user=phoebe)
    bagpipes = Term(term="Bagpipes", parent_id=music.id, user=phoebe)
    singing = Term(term="Singing", parent_id=music.id, user=phoebe)


    db.session.add_all([phoebe, monica, rachel, joey, chandler, ross, star_trek,
                        shut_up_wesley, make_it_so, smellycats, grumpycat, music,
                        guitar, bagpipes, singing])
    db.session.commit()


def connect_to_db(app, uri=None):
    """Connect to db"""

    app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'postgresql:///shnerdy'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    from server import app
    connect_to_db(app, os.environ.get("DATABASE_URL"))
    db.create_all(app=app)
    print "This is in the model file -- you're in the DB"


# For when you forget later but you had to dump and re-do your db:
# db.create_all()
# brew install postgres (if command psql not found)

