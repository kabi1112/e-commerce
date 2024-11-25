from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure your database URI and other configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Example with SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import and register blueprints
    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
