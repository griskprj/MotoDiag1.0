from app.__init__ import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    join_date = db.Column(db.Date, default=datetime.utcnow)
    motorcycles = db.relationship('Motorcycle', back_populates='owner', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password is not readable")
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self._password, password)

class Motorcycle(db.Model):
    __tablename__ = 'motorcycles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='motorcycles')
    brand = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    engine = db.Column(db.Integer, nullable=False)
    moto_type = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.Text)

    @validates('year')
    def validate_year(self, key, year):
        if not 1900 < year <= datetime.now().year:
            raise ValueError("Invalid year")
