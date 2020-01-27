from flask import Flask
from app import api


def create_app():
    app = Flask(__name__)

    with app.app_context():
        from app import routes
        app.register_blueprint(api.api_bp, url_prefix="/api")

    return app
