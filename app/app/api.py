from flask import Blueprint, jsonify, request
from app import db

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
def get_racing_tracks():
    track_id = request.args.get("id")
    name = request.args.get("name")
    city = request.args.get("city")
    country = request.args.get("country")

    racing_tracks = db.get_racing_tracks(track_id, name, city, country)

    return jsonify({
        "data": racing_tracks,
        "total": len(racing_tracks),
        "offset": 0,
        "limit": 50,
    })


@api_bp.route('/measurements')
def get_measurements():
    station_id = request.args.get("station")
    dt1 = request.args.get("dt1")
    dt2 = request.args.get("dt2")
    limit = request.args.get("limit")
    offset = request.args.get("offset")

    measurements, total = db.get_measurements(station_id, dt1, dt2, limit, offset)

    return jsonify({
        "data": measurements,
        "total": total,
        "offset": offset,
        "limit": limit,
    })


@api_bp.route('/measurements/<string:field>/average')
def get_measurement_average(field):
    stations = request.args.get("stations").split(",")
    interval = request.args.get("interval")
    dt1 = request.args.get("dt1")
    dt2 = request.args.get("dt2")
    offset = request.args.get("offset")
    limit = request.args.get("limit")

    measurements, total = db.get_average_measurements(stations, interval, dt1, dt2)

    return jsonify({
        "data": measurements,
        "total": total,
        "offset": offset,
        "limit": limit,
    })
