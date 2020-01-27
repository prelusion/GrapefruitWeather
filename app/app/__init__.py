from flask import Flask
from app import api
from app.db import generate_track_to_station_cache


def create_app():
    app = Flask(__name__)

    with app.app_context():
        generate_track_to_station_cache()
        from app import routes
        app.register_blueprint(api.api_bp, url_prefix="/api")

    return app
