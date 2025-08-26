from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf
from app.utils.helpers import format_currency

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.jinja_env.filters['currency'] = format_currency
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini'
    login_manager.login_message_category = 'warning'
    
    # Register blueprints
    from app.routes import main_bp, api_bp, customer_bp, order_bp, kasbon_bp, payment_bp
    
    app.register_blueprint(main_bp)    
    app.register_blueprint(api_bp)
    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(kasbon_bp, url_prefix="/kasbons")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(payment_bp, url_prefix="/payments")
    # app.register_blueprint(auth_bp)
    
    return app