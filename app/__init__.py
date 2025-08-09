from flask import Flask
from app.extension import db, login_manager, mail, csrf, limiter
from app.models import User
from app.routes import main, auth, moto, maintenance, profile
from app.config import config as cfg

def create_app(config_name='production'):
    app = Flask(__name__)
    app_config = cfg[config_name]
    app.config.from_object(app_config)

    app.serializer = app_config.serializer

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(moto.moto_bp)
    app.register_blueprint(maintenance.maintenance_bp)
    app.register_blueprint(profile.profile_bp)

    with app.app_context():
        db.create_all()

    return app