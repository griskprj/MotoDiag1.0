from flask import Flask, redirect, url_for
from flask_babel import Babel
from app.extension import db, login_manager, mail, csrf, limiter
from app.models import User
from app.routes import main, auth, moto, maintenance, profile, commuinty, errors
from app.config import config as cfg
from app.utils import user_time_ago

def create_app(config_name='production'):
    app = Flask(__name__)
    app_config = cfg[config_name]
    app.config.from_object(app_config)

    app.serializer = app_config.serializer

    app.jinja_env.filters['time_ago'] = user_time_ago.time_ago

    app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    babel = Babel(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
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
    app.register_blueprint(commuinty.community_bp)
    app.register_blueprint(errors.errors_bp)

    @login_manager.unauthorized_handler
    def handle_needs_login():
        return redirect(url_for('auth_bp.login'))

    with app.app_context():
        db.create_all()

    return app