from flask import Blueprint, request, app, session
from flask_login import login_required, login_manager

from app import db
from app import util
from app.util import http_format_error, http_format_data

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
@login_required
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
@login_required
def get_stations():
    longitude = request.args.get("longitude")
    latitude = request.args.get("latitude")
    track_id = request.args.get("track_id")
    radius = request.args.get("radius")
    country_id = request.args.get("country")
    limit = request.args.get("limit")
    result = []

    if track_id:
        if country_id:
            print("track_id, country_id")
            result = db.get_stations_for_track_by_country_id(track_id, country_id, radius)
        elif limit:
            print("track_id, limit")
            result = db.get_stations_for_track_id_by_limit(track_id, limit)
    elif latitude and longitude:
        print("latitude and longitude")
        if limit is None:
            limit = 50
        result = db.get_stations_by_coordinates(latitude, longitude, limit)
    else:
        return http_format_error("Invalid parameters")

    params = {
        "limit": limit,
        "offset": limit,
        "total": len(result),
    }

    if not result:
        return http_format_error("Unable to retrieve data")

    return http_format_data(result, params)


@api_bp.route('/measurements/airpressure')
@login_required
def get_airpressure_measurements():
    """
    Example: http://127.0.0.1:5000/api/measurements/airpressure?limit=120&stations=93590,589210


    To convert measurement timestamps to browser timezone:

        Execute in javascript:
            offset = new Date().getTimezoneOffset();

        Call timezone api with offset:
            timezone_id = http://127.0.0.1:5000/api/timezone?offset=<offset>

        Call air pressure api with timezone id:
            http://127.0.0.1:5000/api/measurements/airpressure?limit=120&stations=93590,589210&timezone=timezone_id


    To convert measurement timestamps to F1 circuit timezone:

        Call timezone api with F1 track id:
            timezone_id = http://127.0.0.1:5000/api/timezone?track_id=<track_id>

        Call air pressure api with timezone id:
            http://127.0.0.1:5000/api/measurements/airpressure?limit=120&stations=93590,589210&timezone=timezone_id
    """

    def convert_measurement(measurement, timezone):
        dt, value = measurement
        return util.utc_to_local(dt, timezone), value

    stations = request.args.get("stations", [743700, 93590, 589210])

    if isinstance(stations, str):
        try:
            stations = stations.split(",")
        except AttributeError:
            stations = [stations]

    stations = list(map(int, stations))
    interval = int(request.args.get("interval", 1))
    limit = int(request.args.get("limit", 120))
    timezone_id = request.args.get("timezone")

    measurements = db.get_most_recent_air_pressure_average(stations, limit, interval)

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        measurements = list(map(
            lambda measurement: convert_measurement(measurement, timezone["name"]), measurements))

    params = {
        "total": len(measurements),
        "limit": limit,
        "interval": interval,
        "stations": stations,
    }

    return http_format_data(measurements, params)


@api_bp.route('/timezone')
@login_required
def get_timezone():
    """
    offset parameter must be given in the format returned by the following
    javascript command:

        new Date().getTimezoneOffset();

    The time-zone offset is the difference, in minutes, between UTC and local time.
    Note that this means that the offset is positive if the local timezone is behind
    UTC and negative if it is ahead. For example, if your time zone is UTC+10
    (Australian Eastern Standard Time), -600 will be returned. Daylight savings time
    prevents this value from being a constant even for a given locale.
    """

    def convert_js_offset_to_storage_offset(offset_mins):
        offset_hours = offset_mins / 60
        offset_opposite = offset_hours * -1
        offset_times_hundred = offset_opposite * 100
        offset_rounded = int(offset_times_hundred)
        offset_padded = str(offset_rounded).zfill(5 if offset_rounded < 0 else 4)

        if int(offset_rounded) > 0:
            return "+" + offset_padded

        return offset_padded

    station_id = request.args.get("station_id")
    track_id = request.args.get("track_id")
    timezone_id = request.args.get("timezone_id")
    offset = request.args.get("offset")

    if not util.only_one_is_true(station_id, track_id, timezone_id, offset):
        return http_format_error("Only one query parameter can be used simultaneously")

    timezone = None

    if station_id:
        timezone = db.get_timezone_by_station_id(station_id)
    elif track_id:
        timezone = db.get_timezone_by_track_id(track_id)
    elif timezone_id:
        # TODO create get_timezone_offset_by_timezone_id function
        # success, result = db.get_timezone_offset_by_timezone_id(timezone_id)
        return http_format_error("Not implemented yet")
    elif offset:
        offset = convert_js_offset_to_storage_offset(int(offset))
        timezone = db.get_timezone_by_offset(offset)

    if not timezone:
        return http_format_error("Invalid input")

    return http_format_data(timezone)