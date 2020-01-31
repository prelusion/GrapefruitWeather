import json
import time
from datetime import datetime

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
    station_id = request.args.get("id")
    longitude = request.args.get("longitude")
    latitude = request.args.get("latitude")
    track_id = request.args.get("track_id")
    radius = request.args.get("radius")
    country = request.args.get("country")
    limit = request.args.get("limit")
    timezone = request.args.get("timezone")
    offset = request.args.get("offset")

    success, result = db.get_stations(station_id=station_id,
                                      longitude=longitude,
                                      latitude=latitude,
                                      track_id=track_id,
                                      radius=radius,
                                      country=country,
                                      limit=limit,
                                      timezone=timezone,
                                      offset=offset
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
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [743700, 93590, 589210]))))
    interval = int(request.args.get("interval", 1))
    limit = int(request.args.get("limit", 120))
    timezone_id = request.args.get("timezone")

    measurements = db.get_most_recent_air_pressure_average(stations, limit, interval)

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        measurements = list(map(
            lambda measurement: util.convert_single_field_measurement_timezone(
                measurement, timezone["name"]), measurements))

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


@api_bp.route('/measurements/export/json')
def create_measurements_export():
    hours = int(request.args.get("hours", 1))
    timezone_id = request.args.get("timezone")
    fields = util.convert_array_param(
        request.args.get("fields", ["temperature", "air_pressure"]))
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [743700, 93590, 589210]))))

    if "station_id" not in fields:
        fields.append("station_id")

    tstart = time.time()
    measurements = db.get_all_measurements(stations, fields, hours)
    duration = time.time() - tstart

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        #  TODO timezone conversion

    params = {
        "total": len(measurements),
        "hours": hours,
        "stations": stations,
        "duration": duration,
    }

    return http_format_data(measurements, params)


@api_bp.route('/measurements/export/file', methods=['GET'])
def get_measurements_export():
    hours = int(request.args.get("hours", 1))
    timezone_id = request.args.get("timezone")
    fields = util.convert_array_param(
        request.args.get("fields", ["temperature", "air_pressure"]))
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [743700, 93590, 589210]))))

    if "station_id" not in fields:
        fields.append("station_id")

    measurements = db.get_all_measurements(stations, fields, hours)

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        #  TODO timezone conversion

    content = json.dumps(measurements, indent=4, sort_keys=True, default=str)

    export_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return Response(
        content,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment;filename={export_id}.json'})


@api_bp.route('/measurements/temperature')
@login_required
def get_temperature_measurements():
    stations = list(map(int, util.convert_array_param(
        request.args.get("stations", [85210]))))
    interval = int(request.args.get("interval", 1))  # hours
    limit = int(request.args.get("limit", 1200))
    offset = int(request.args.get("offset", 0))
    timezone_id = request.args.get("timezone")

    measurements = db.get_most_recent_temperature_averages(stations, limit, interval, offset)

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        measurements = list(map(
            lambda measurement: util.convert_single_field_measurement_timezone(
                measurement, timezone["name"]), measurements))

    params = {
        "total": len(measurements),
        "limit": limit,
        "interval": interval,
        "stations": stations,
    }

    return http_format_data(measurements, params)
