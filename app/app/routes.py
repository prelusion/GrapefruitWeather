from flask import current_app as app, request, url_for, redirect, make_response, session
from flask_login import login_user, login_required

from app import db, get_user
from flask import render_template, send_from_directory
import os


@app.route("/")
@login_required
def index():
    racing_tracks = db.get_racing_tracks()[1];
    return render_template('index.html', racing_tracks=racing_tracks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = get_user(username=request.form["username"])
        if user is not False and user.password == request.form["password"]:
            login_user(user)
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
