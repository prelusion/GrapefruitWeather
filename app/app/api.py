from flask import Blueprint, jsonify, request
from app import db

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
def get_racing_tracks():
    track_id = request.args.get("id")
    name = request.args.get("name")
    city = request.args.get("city")
    country = request.args.get("country")

    success, result = db.get_racing_tracks(track_id, name, city, country)

    if success is False:
        return create_error(result)
    else:
        return format_data(result)


@api_bp.route('/stations')
def get_stations():
    station_id = request.args.get("id")
    longitude = request.args.get("longitude")
    latitude = request.args.get("latitude")
    radius = request.args.get("radius")
    country = request.args.get("country")

    success, result = db.get_stations(station_id, longitude, latitude, radius, country)

    if success is False:
        return create_error(result)
    else:
        return format_data(result)


def create_error(message):
    return jsonify({
        "error": message
    })


def format_data(data):
    return jsonify({
        "data": data,
        "total": len(data),
        "offset": 0,
        "limit": 50,
    })
