"""
Flask application configuration and initialization.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app(config_overrides: dict | None = None):
    """Factory function to create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    )

    # Configure the SQLite database, relative to the project root
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'project.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "another-super-secret-key"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max file size

    if config_overrides:
        app.config.update(config_overrides)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.end_user.login"
    login_manager.login_message = "Por favor inicie sesión para acceder a esta página."
    login_manager.login_message_category = "error"

    return app


# Create the app instance
app = create_app()
