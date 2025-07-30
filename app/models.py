from flask_login import UserMixin
import datetime
from extenshions import db

friends_association = db.Table(
    'friends_association',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
)
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    join_date = db.Column(db.Date, default=datetime.date.today)
    motorcycles = db.relationship('Motorcycle', backref='owner', lazy=True)

    friends = db.relationship(
        'User',
        secondary=friends_association,
        primaryjoin=(id == friends_association.c.user_id),
        secondaryjoin=(id == friends_association.c.friend_id),
        backref='friend_of'
    )

class Motorcycle(db.Model):
    __tablename__ = 'motorcycles'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    moto_type = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Date, nullable=False)
    photo = db.Column(db.LargeBinary)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
