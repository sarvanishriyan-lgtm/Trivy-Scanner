from flask import Flask
from flask_cors import CORS

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    CORS(app)

    # Import and register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app