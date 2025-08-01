from app import db, login_manager
from flask_login import UserMixin
import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    join_date = db.Column(db.Date, default=datetime.date.today)

    motorcycles = db.relationship('Motorcycle', backref='owner', lazy=True)


class Motorcycle(db.Model):
    __tablename__ = 'motorcycles'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    moto_type = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Date, nullable=False)
    photo = db.Column(db.LargeBinary)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
