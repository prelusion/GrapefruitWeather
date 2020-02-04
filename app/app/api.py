from datetime import datetime

from dicttoxml import dicttoxml
from flask import Blueprint, request, Response
from flask_login import login_required

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
            result = db.get_stations_for_track_by_country_id(track_id, country_id, radius)
        elif limit:
            result = db.get_stations_for_track_id_by_limit(track_id, limit)
    elif latitude and longitude:
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
    station_id = request.args.get("station_id")
    track_id = request.args.get("track_id")
    offset = request.args.get("offset")

    if not util.only_one_is_true(station_id, track_id, offset):
        return http_format_error("Only one query parameter can be used simultaneously")

    timezone = None

    if station_id:
        timezone = db.get_timezone_by_station_id(station_id)
    elif track_id:
        timezone = db.get_timezone_by_track_id(track_id)
    elif offset:
        offset = util.convert_js_offset_to_storage_offset(int(offset))
        timezone = db.get_timezone_by_offset(offset)

    if not timezone:
        return http_format_error("Failed to retrieve timezone")

    return http_format_data(timezone)


@api_bp.route('/measurements/airpressure')
@login_required
def get_airpressure_measurements():
    """
    Example: http://127.0.0.1:5000/api/measurements/airpressure?limit=120&stations=93590,589210
    """
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [743700, 93590, 589210]))))
    limit = int(request.args.get("limit", 120))
    timezone_offset = request.args.get("timezone")

    timezone_name = None
    if timezone_offset is not None:
        offset = util.convert_js_offset_to_storage_offset(int(timezone_offset))
        timezone = db.get_timezone_by_offset(offset)
        timezone_name = timezone["name"]

    measurements = db.get_most_recent_air_pressure_average(stations, limit,  timezone_name)

    params = {
        "total": len(measurements),
        "limit": limit,
        "stations": stations,
    }

    return http_format_data(measurements, params)


@api_bp.route('/measurements/temperature')
@login_required
def get_temperature_measurements():
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [85210]))))
    limit = int(request.args.get("limit", 24 * 7))
    timezone_offset = request.args.get("timezone")

    timezone_name = None
    if timezone_offset is not None:
        offset = util.convert_js_offset_to_storage_offset(int(timezone_offset))
        timezone_name = db.get_timezone_by_offset(offset)["name"]

    measurements = db.get_most_recent_temperature_averages(stations, limit, timezone_name)

    params = {
        "total": len(measurements),
        "limit": limit,
        "stations": stations,
    }

    return http_format_data(measurements, params)


@api_bp.route('/measurements/export/xml', methods=['GET'])
def get_measurements_export():
    """
    timzone parameter must be given in the format returned by the following
    javascript command:

        new Date().getTimezoneOffset();
    """
    def convert_measurement(measurement, timezone):
        dt, value = measurement
        return {
            "utc_timestamp": dt,
            "value": value,
        }

    air_stations = list(map(int, util.convert_array_param(
        request.args.get("pressurestations", [743700, 93590, 589210]))))
    temp_stations = list(map(int, util.convert_array_param(
        request.args.get("tempstations", [743700, 93590, 589210]))))
    timezone_offset = request.args.get("timezone")

    timezone_name = None
    if timezone_offset is not None:
        offset = util.convert_js_offset_to_storage_offset(int(timezone_offset))
        timezone_name = db.get_timezone_by_offset(offset)["name"]

    air_measurements = db.get_most_recent_air_pressure_average(air_stations, 120)
    temp_measurements = db.get_most_recent_temperature_averages(temp_stations, 24 * 7)

    air_measurements = map(lambda m: convert_measurement(m, timezone_name), air_measurements)
    temp_measurements = map(lambda m: convert_measurement(m, timezone_name), temp_measurements)

    body = {
        "air_pressure": air_measurements,
        "temperature": temp_measurements,
    }

    content = dicttoxml(body, custom_root='measurements', attr_type=False,
                        item_func=lambda parent: "measurement")
    export_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return Response(
        content,
        mimetype='text/xml',
        headers={'Content-Disposition': f'attachment;filename={export_id}.xml'})
