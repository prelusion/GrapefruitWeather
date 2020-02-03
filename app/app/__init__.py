from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from app import api
from app.db import generate_track_to_station_cache
import logging

from app.fileaccess import get_user, get_tracks, get_track_distances

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    cors = CORS(app,  resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        from app import routes

        app.register_blueprint(api.api_bp, url_prefix="/api")
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "/login"
        @login_manager.user_loader
        def load_user(user_id):
            return get_user(user_id)

        app.secret_key = "CDDA3AEBE6A9DF4757AE5175391BA"

        logger.info("Generating distances for tracks... this takes one to two minutes")
        generate_track_to_station_cache()
        logger.info("Generating distances for tracks succesful, caching data for next time")

        for track in get_tracks():
            get_track_distances(track["id"])

    return app
