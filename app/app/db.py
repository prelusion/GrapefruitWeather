import datetime
from copy import deepcopy

import pytz
from geopy import distance
from app import fileaccess
from app import wsmc
from app.fileaccess import generate_track_distance_cache, get_track_distances


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
        racing_tracks = limit_and_offset(racing_tracks, limit, offset)
    except ValueError:
        return False, "Invalid limit given."

    return True, racing_tracks


def get_stations(station_id=None,
                 longitude=None,
                 latitude=None,
                 track_id=None,
                 radius=None,
                 country=None,
                 limit=50,
                 timezone=None,
                 offset=None
                 ):

    def remove_empty_locals():
        parameters = locals()
        for local in parameters:
            if local is not None:
                if local == "":
                    local = None
                    remove_empty_locals()
                    return

    stations = deepcopy(fileaccess.get_stations())

    if radius is not None and (latitude is not None or longitude is not None):
        return False, "Latitude or longitude not set."

    if station_id is not None:
        stations = list(filter(lambda station: int(station["id"]) == int(station_id), stations))

    if country is not None:
        stations = list(filter(lambda station: station["country-id"].lower() == country.lower(), stations))

    for station in stations:
        if not timezone:
            station.pop("timezone")

        if longitude is not None and latitude is not None:
            target_location = [float(latitude), float(longitude)]
            station["distance"] = round(
                distance.distance([float(station["latitude"]), float(station["longitude"])],
                                  target_location).km)
    if track_id and (int(track_id) < 23):
        distances = get_track_distances(track_id)
        stations = stations[:limit]
        for _station in stations:
            _station["distance"] = distances[_station["id"]]

    if longitude is not None and latitude is not None:
        stations.sort(key=lambda station: station["distance"])

    if longitude is not None and latitude is not None and radius is not None:
        stations = list(filter(lambda station: station["distance"] < float(radius), stations))

    try:
        stations = limit_and_offset(stations, limit, offset)
    except ValueError:
        return False, "Invalid limit given."

    return True, stations


def get_most_recent_air_pressure_average(station_ids, seconds, interval):
    rawdata = wsmc.read_test_file()
    measurementbytes_generator = wsmc.iterate_dataset_left(rawdata)
    measurementbytes_generator = wsmc.filter_by_field(
        measurementbytes_generator, "station_id", station_ids)
    measurementbytes_generator = wsmc.filter_most_recent(
        measurementbytes_generator, seconds)
    measurement_generator = wsmc.group_by_timestamp(
        measurementbytes_generator, interval)
    avg_temperatures = list(
        wsmc.groups_to_average("air_pressure", measurement_generator))
    return avg_temperatures


def get_timezone_by_station_id(station_id):
    stations = get_stations(station_id=station_id, timezone=True)
    if len(stations[1]) != 1:
        return False, "Invalid station returned."
    return True, stations[1][0]["timezone"]


def get_timezone_by_track_id(track_id):

    tracks = get_racing_tracks(track_id=track_id)
    if len(tracks[1]) != 1:
        return False, "Invalid track returned."
    return True, tracks[1][0]["timezone"]


def get_timezone_by_timezone_id(timezone_id):
    timezones = fileaccess.get_timezones()
    for timezone in timezones:
        if timezone_id == timezone["id"]:
            return True, timezone
    return False, "ID not found."


def limit_and_offset(dataset, limit, offset):
    if limit is None or "":
        from app.const import DEFAULT_LIMIT
        limit = DEFAULT_LIMIT
    else:
        limit = int(limit)

    if offset is None:
        offset = 0
    else:
        offset = int(offset)

    new_data_set = []
    for i in range(limit + offset):
        if (i + offset + 1) > len(dataset):
            break;
        new_data_set.append(dataset[i + offset])
    return new_data_set


def convert_tz(measurements, source_tz, dest_tz):
    for measurement in measurements:
        measurement = pytz.timezone(pytz.timezone(source_tz)).localize(measurement)
        measurement = measurement[0].astimezone(pytz.timezone(dest_tz))
    return measurements


def generate_track_to_station_cache():
    success, tracks = get_racing_tracks()

    for track in tracks:
        distances = []
        success, stations = get_stations(limit=16000)
        for station in stations:
            _distance = round(distance.distance([float(track["latitude"]), float(track["longitude"])],
                                    (float(station["latitude"]), float(station["longitude"]))).km)
            distances.append((station["id"], _distance))
        distances.sort(key=lambda distances: distances[0])
        generate_track_distance_cache(distances, track["id"])