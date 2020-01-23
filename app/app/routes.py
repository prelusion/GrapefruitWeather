from flask import current_app as app
from flask import render_template

from app import db


@app.route("/")
def index():
    racing_tracks = db.get_racing_tracks()[1];
    weather_stations = db.get_stations();
    return render_template('index.html', racing_tracks=racing_tracks, weather_stations=weather_stations)
