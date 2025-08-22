from app.extension import db
from flask_login import UserMixin
from datetime import datetime

''' PENDING USER REGISTER '''
class PendingRegistration(db.Model):
    __tablename__ = 'pending_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    verification_token = db.Column(db.String(32), nullable=False)
    token_expiration = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('username', name='uq_pending_username'),
    )

''' USER '''
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_reg = db.Column(db.Integer, default=1)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(100), unique=True)
    confirmation_sent_at = db.Column(db.DateTime)
    image = db.Column(db.LargeBinary)

    subscriptions = db.relationship(
        'Subscription',
        foreign_keys='Subscription.subscriber_id',
        backref='subscriber',
        lazy='dynamic'
    )
    subscribers = db.relationship(
        'Subscription',
        foreign_keys='Subscription.subscribed_to_id',
        backref='subscribed_to',
        lazy='dynamic'
    )

    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('confirmation_token', name='uq_user_confirmation_token'),
    )

''' SUBSCRIPTIONS '''
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscribed_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_subscribed = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('subscriber_id', 'subscribed_to_id', name='uq_subscription_pair'),
    )

''' MOTORCYCLE '''
class Motorcycle(db.Model):
    __tablename__ = 'motorcycles'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    model = db.Column(db.String(120), nullable=False)
    years_create = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    last_mileage_update = db.Column(db.DateTime, default=datetime.utcnow)
    moto_type = db.Column(db.String, nullable=False)
    engine_volume = db.Column(db.Integer, nullable=False)
    drive_type = db.Column(db.String(20), nullable=False, default="chain")
    condition = db.Column(db.String(40), nullable=False, default="Отличное")
    image = db.Column(db.LargeBinary)

''' ELEMENTS AND FLUID '''
class ElementsFluid(db.Model):
    __tablename__ = 'elements_fluids'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    moto_id = db.Column(db.Integer, nullable=False)
    brake_fluid = db.Column(db.Boolean, default=False)
    oil_filter = db.Column(db.Boolean, default=False)
    air_filter = db.Column(db.Boolean, default=False)
    spark_plug = db.Column(db.Boolean, default=False)
    drive_maintenance = db.Column(db.Boolean, default=False)
    drive_change = db.Column(db.Boolean, default=False)
    brake_fluid_date = db.Column(db.DateTime)
    oil_filter_date = db.Column(db.DateTime)
    air_filter_date = db.Column(db.DateTime)
    spark_plug_date = db.Column(db.DateTime)
    drive_maintenance_date = db.Column(db.DateTime)
    drive_change_date = db.Column(db.DateTime)
    brake_fluid_mileage = db.Column(db.Integer, default=0)
    oil_filter_mileage = db.Column(db.Integer, default=0)
    air_filter_mileage = db.Column(db.Integer, default=0)
    spark_plug_mileage = db.Column(db.Integer, default=0)
    drive_maintenance_mileage = db.Column(db.Integer, default=0)
    drive_change_mileage = db.Column(db.Integer, default=0)

''' MAINTENANCE HISTORY'''
class MaintenanceHistory(db.Model):
    __tablename__ = 'maintenance_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    moto_id = db.Column(db.Integer, nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Integer)
    notes = db.Column(db.Text)
    image = db.Column(db.LargeBinary)

''' PASSWORD RESET TOKEN '''
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(200), nullable=False)
    token_expiration = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('token', name='uq_password_reset_token'),
    )