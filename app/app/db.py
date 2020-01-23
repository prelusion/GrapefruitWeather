from copy import deepcopy

from geopy import distance

from app import fileaccess
from app import wsmc
from app.const import RACING_TRACKS
from app.util import limit_and_offset


def get_racing_tracks(track_id=None, name=None, city=None, country=None, limit=None, offset=None):
    racing_tracks = deepcopy(RACING_TRACKS)

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
                 radius=None,
                 country=None,
                 limit=50,
                 timezone=None,
                 offset=None
                 ):
  
    parameters = locals()
    for local in parameters:
        if local is not None:
            if local == "":
                local = None

    stations = deepcopy(fileaccess.get_stations_db())

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
