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


@api_bp.route('/stations')
def get_stations():
    station_id = request.args.get("id")
    longitude = request.args.get("longitude")
    latitude = request.args.get("latitude")
    radius = request.args.get("radius")
    country = request.args.get("country")
    limit = request.args.get("limit")
    timezone = request.args.get("timezone")
    offset = request.args.get("offset")

    success, result = db.get_stations(station_id=station_id,
                                      longitude=longitude,
                                      latitude=latitude,
                                      radius=radius,
                                      country=country,
                                      limit=limit,
                                      offset=offset,
                                      timezone=timezone
                                      )

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


@api_bp.route('/airpressure')
def get_most_recent_air_pressure():
    stations = request.args.get("stations",  [743700, 93590, 589210])
    interval = request.args.get("interval", 1)
    limit = request.args.get("limit", 120)

    measurements = db.get_most_recent_air_pressure_average(stations, limit, interval)

    return jsonify({
        "params": {
            "stations": stations,
            "limit": limit,
            "interval": interval,
        },
        "data": measurements,
        "total": len(measurements),
        "offset": 0,
        "limit": 0,
    })
