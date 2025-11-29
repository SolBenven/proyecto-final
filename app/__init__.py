from flask import Flask
from app.extensions import db
from app.routes.main import main_bp


def create_app():
    app = Flask(__name__)

    # Configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the extension
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)

    return app
