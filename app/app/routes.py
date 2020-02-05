import os

from flask import current_app as app, request, redirect, render_template, send_from_directory
from flask_login import login_user, login_required, logout_user
from passlib.hash import argon2

from app import db, fileaccess


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if "logout" in request.form:
            logout_user()
            return redirect("/login")
    racing_tracks = db.get_racing_tracks()[1];
    return render_template('index.html', racing_tracks=racing_tracks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        user = fileaccess.get_user(username=request.form["username"])
        if user is not False and argon2.verify(request.form["password"], user.password):
            login_user(user)
            return redirect("/")

        error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
