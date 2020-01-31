import os
from copy import deepcopy
from logging import getLogger
from pprint import pprint
from geopy import distance

from app import const
from app import weatherdata
from app import fileaccess
from app import util

logger = getLogger(__name__)


def get_racing_tracks(track_id=None, name=None, city=None, country=None, limit=None, offset=None):
    racing_tracks = fileaccess.get_tracks()

    if track_id is not None:
        racing_tracks = list(filter(lambda track: track["id"] == int(track_id), racing_tracks))
    if name is not None:
        racing_tracks = list(filter(lambda track: track["title"].lower() == name.lower(), racing_tracks))
    if city is not None:
        racing_tracks = list(
            filter(lambda track: track["city"] is not None and track["city"].lower() == city.lower(),
                   racing_tracks))
    if country is not None:
        racing_tracks = list(filter(lambda track: track["country"].lower() == country.lower(), racing_tracks))

    try:
        racing_tracks = util.limit_and_offset(racing_tracks, limit, offset)
    except ValueError:
        return False, "Invalid limit given."

    return True, racing_tracks


def get_stations(station_id=None, longitude=None, latitude=None, track_id=None,
                 radius=None, country=None, limit=50, timezone=None, offset=None):
    def remove_empty_locals():
        parameters = locals()
        for local in parameters:
            if local is not None:
                if local == "":
                    local = None
                    remove_empty_locals()
                    return

    if limit is None:
        limit = 50

    stations = deepcopy(fileaccess.get_stations())

    if radius is not None and (latitude is not None or longitude is not None):
        return False, "Latitude or longitude not set."

    if station_id is not None:
        stations = list(filter(lambda st: int(st["id"]) == int(station_id), stations))

    if country is not None:
        stations = list(filter(lambda st: st["country-id"].lower() == country.lower(), stations))

    for station in stations:
        if not timezone:
            station.pop("timezone")

        if longitude is not None and latitude is not None:
            target_location = [float(latitude), float(longitude)]
            station["distance"] = round(
                distance.distance([float(station["latitude"]), float(station["longitude"])],
                                  target_location).km)

    if track_id and (int(track_id) < 23):
        distances = fileaccess.get_track_distances(track_id)
        for _station in stations:
            _station["distance"] = int(distances[_station["id"]])
        stations.sort(key=lambda st: st["distance"])
        stations = stations[:int(limit)]
        if radius and int(radius) > 0:
            stations = list(filter(lambda station: station["distance"] < float(radius), stations))

    if longitude is not None and latitude is not None:
        stations.sort(key=lambda st: st["distance"])

    if longitude is not None and latitude is not None and radius is not None:
        stations = list(filter(lambda st: st["distance"] < float(radius), stations))

    try:
        stations = util.limit_and_offset(stations, limit, offset)
    except ValueError:
        return False, "Invalid limit given."

    return True, stations





def get_timezone_by_station_id(station_id):
    success, result = get_stations(station_id=station_id, timezone=True)

    if success and len(result) == 1:
        return result[0]["timezone"]


def get_timezone_by_track_id(track_id):
    success, result = get_racing_tracks(track_id=track_id)

    if success and len(result) == 1:
        return result[0]["timezone"]


def get_timezone_by_timezone_id(timezone_id):
    timezones = fileaccess.get_timezones()
    for timezone in timezones:
        if timezone_id == timezone["id"]:
            return timezone


def get_timezone_by_offset(offset):
    timezones = fileaccess.get_timezones()

    for timezone in timezones:
        if offset == timezone["offset"]:
            return timezone


def generate_track_to_station_cache(force=False):
    success, tracks = get_racing_tracks()

    for track in tracks:
        file_path = const.TRACK_CACHE_DIR + "/" + str(track["id"]) + ".csv"
        if os.path.isfile(file_path) or force:
            continue
        logger.info(f"Generating distances for track {track['id']}")
        distances = []
        success, stations = get_stations(limit=16000)
        for station in stations:
            _distance = round(distance.distance([float(track["latitude"]), float(track["longitude"])],
                                                (float(station["latitude"]), float(station["longitude"]))).km)
            distances.append((station["id"], _distance))
        distances.sort(key=lambda dist: dist[0])
        fileaccess.generate_track_distance_cache(distances, track["id"])


def get_all_measurements(station_ids, fields, hours):
    result = []
    offset = 0
    extension = weatherdata.WSMC_EXTENSION

    while True:
        print("offset:", offset)
        rawdata = weatherdata.load_data_per_file(const.MEASUREMENTS_DIR, offset, extension)

        if len(rawdata) == 0:
            break

        measurementbytes_generator = weatherdata.iterate_dataset_left(rawdata, extension)
        measurementbytes_generator = weatherdata.filter_by_field(
            measurementbytes_generator, "station_id", station_ids, extension)
        measurementbytes_generator = weatherdata.filter_most_recent(
            measurementbytes_generator, hours * 60 * 60, extension)
        newresult = list(weatherdata.decode_measurement_fields(measurementbytes_generator, fields, extension))

        result.extend(newresult)

        offset += 1

    return result


def get_most_recent_air_pressure_average(station_ids, limit, interval):
    result = []
    offset = 0
    extension = weatherdata.WSMC_EXTENSION

    while limit > 0:
        data = weatherdata.load_data_per_file(const.MEASUREMENTS_DIR, offset, extension)

        if len(data) == 0:
            break

        measurementbytes_generator = weatherdata.iterate_dataset_left(data, extension)
        measurementbytes_generator = weatherdata.filter_by_field(
            measurementbytes_generator, "station_id", station_ids, extension)
        measurementbytes_generator = weatherdata.filter_most_recent(
            measurementbytes_generator, limit, extension)
        measurement_generator = weatherdata.group_by_timestamp(
            measurementbytes_generator, interval, extension)
        newresult = list(
            weatherdata.groups_to_average("air_pressure", measurement_generator))

        result.extend(newresult)
        limit -= len(newresult)

        offset += 1

    return result


def get_most_recent_temperature_averages(station_ids, limit, interval_hours, offset):
    result = []
    offset = 0
    extension = weatherdata.WSAMC_EXTENSION
    interval_seconds = interval_hours * 3600

    while limit > 0:
        data = weatherdata.load_data_per_file(const.MEASUREMENTS_DIR, offset, extension)

        if len(data) == 0:
            break

        measurementbytes_generator = weatherdata.iterate_dataset_left(data, extension)
        measurementbytes_generator = weatherdata.filter_most_recent(
            measurementbytes_generator, limit, extension)
        measurement_generator = weatherdata.group_by_timestamp(
            measurementbytes_generator, interval_seconds, extension)
        newresult = list(
            weatherdata.groups_to_average("temperature", measurement_generator))

        result.extend(newresult)
        limit -= len(newresult)

        offset += 1

    return result
