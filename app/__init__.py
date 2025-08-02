from flask import Flask
from app.extensions import db, login_manager
from flask_migrate import Migrate
from app.config import Config

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app import models
    with app.app_context():
        db.create_all()
    
    # Регистрация blueprint
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    return app
