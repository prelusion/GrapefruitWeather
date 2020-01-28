from flask import Flask
from flask_login import LoginManager

from app import api
from app.db import generate_track_to_station_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    with app.app_context():
        from app import routes
        app.register_blueprint(api.api_bp, url_prefix="/api")
        login_manager = LoginManager()
        login_manager.init_app(app)
        logger.info("Generating distances for tracks... this takes one to two minutes")
        generate_track_to_station_cache()
        logger.info("Generating distances for tracks succesful, caching data for next time")
    return app
