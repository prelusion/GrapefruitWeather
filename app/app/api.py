from flask import Blueprint, request

from app import db
from app.util import http_format_error, http_format_data

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
def get_racing_tracks():
    track_id = request.args.get("id")
    name = request.args.get("name")
    city = request.args.get("city")
    country = request.args.get("country")

    success, result = db.get_racing_tracks(track_id, name, city, country)

    params = {
        "total": len(result),
    }

    if success is False:
        return http_format_error(result)
    else:
        return http_format_data(result, params)


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

    params = {
        "total": len(result),
        "limit": limit,
        "offset": limit,
    }

    if success is False:
        return http_format_error(result)
    else:
        return http_format_data(result, params)


@api_bp.route('/measurements/airpressure')
def get_airpressure_measurements():
    """
    Example: http://127.0.0.1:5000/api/measurements/airpressure?limit=120&stations=93590,589210
    """
    stations = request.args.get("stations", [743700, 93590, 589210])
    try:
        stations = stations.split(",")
    except IndexError:
        stations = stations
    stations = list(map(int, stations))
    interval = int(request.args.get("interval", 1))
    limit = int(request.args.get("limit", 120))

    measurements = db.get_most_recent_air_pressure_average(stations, limit, interval)

    params = {
        "total": len(measurements),
        "limit": limit,
        "interval": interval,
        "stations": stations,
    }

    return http_format_data(measurements, params)
