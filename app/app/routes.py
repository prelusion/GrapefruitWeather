from flask import current_app as app
from flask import render_template

from app import db


@app.route("/")
def index():
    racing_tracks = db.get_racing_tracks()[1];
    return render_template('index.html', racing_tracks=racing_tracks)

@app.route("/login")
def login():
    return render_template('login.html')
