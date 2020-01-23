import datetime
import math
import os
from collections import OrderedDict

from app import const
from app import util

PREFERRED_CHUNK_SIZE = 104857600  # +- 100 MB

# Byte count for each field within a measurement
PROTOCOL_FORMAT_BC = OrderedDict({
    "station_id": 3,
    "timestamp": 4,
    "null_indication": 2,
    "temperature": 3,
    "dew_point": 3,
    "air_pressure": 3,
    "sea_air_pressure": 3,
    "visibility": 2,
    "air_speed": 2,
    "rainfall": 3,
    "snowfall": 2,
    "events": 1,
    "cloud_pct": 2,
    "wind_direction": 2,
})

# Starting byte for each field within a measurement
PROTOCOL_FORMAT_BS = OrderedDict({
    "station_id": 0,
    "timestamp": 3,
    "null_indication": 7,
    "temperature": 9,
    "dew_point": 12,
    "air_pressure": 15,
    "sea_air_pressure": 18,
    "visibility": 21,
    "air_speed": 23,
    "rainfall": 25,
    "snowfall": 28,
    "events": 30,
    "cloud_pct": 31,
    "wind_direction": 33,
})

MEASUREMENT_BYTE_COUNT = sum(PROTOCOL_FORMAT_BC.values())
CHUNKS = math.trunc(PREFERRED_CHUNK_SIZE / MEASUREMENT_BYTE_COUNT)
ACTUAL_CHUNK_SIZE = CHUNKS * MEASUREMENT_BYTE_COUNT


def read_test_file():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    return read_file(filepath, ACTUAL_CHUNK_SIZE)


def read_file(filepath, bytecount=None):
    with open(filepath, "rb") as f:
        if bytecount:
            data = f.read(bytecount)
        else:
            data = f.read()

    if len(data) % MEASUREMENT_BYTE_COUNT != 0:
        raise Exception("wsmc file is corrupt")

    return data


def decode_field(field, data):
    decoded = int.from_bytes(data, byteorder="big", signed=True)

    if field == "station_id":
        return decoded
    if field == "timestamp":
        return datetime.datetime.utcfromtimestamp(decoded)
    if field == "rainfall":
        return decoded / 100
    if field == "wind_direction":
        return decoded
    if field == "events" or field == "null_indication":
        return format(decoded, "b")
    if field in ("temperature", "dew_point", "air_pressure", "sea_air_pressure",
                 "visibility", "air_speed", "snowfall", "cloud_pct"):
        return decoded / 10
    else:
        raise ValueError("Unnown field")


def decode_measurement(bindata):
    measurement = OrderedDict()
    i = 0

    for field, bytecount in PROTOCOL_FORMAT_BC.items():
        measurement[field] = decode_field(field, bindata[i:i + bytecount])
        i += bytecount

    return measurement


def iterate_dataset_left(data):
    """ Each iteration the value of the given fieldname is yielded. """
    i = len(data)
    while i > 0:
        measurementaddr = (i - MEASUREMENT_BYTE_COUNT)
        yield data[measurementaddr:measurementaddr + MEASUREMENT_BYTE_COUNT]
        i -= MEASUREMENT_BYTE_COUNT


def filter_by_field(measurementbytes_generator, fieldname, values):
    fieldaddr = PROTOCOL_FORMAT_BS[fieldname]
    field_bc = PROTOCOL_FORMAT_BC[fieldname]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        decoded = decode_field(fieldname, bytevalue)

        if decoded in values:
            yield measurementbytes


def filter_by_timestamp(measurementbytes_generator, dt1, dt2):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if dt1 < timestamp <= dt2:
            yield decode_measurement(bytevalue)
        elif timestamp < dt1:
            break


def filter_most_recent(measurementbytes_generator, seconds):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]
    first = None

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if not first:
            first = timestamp

        if timestamp < first - datetime.timedelta(seconds=seconds):
            break

        yield measurementbytes


def group_by_timestamp(measurementbytes_generator, interval):
    measurements = []
    currtimestamp = None

    for measurementbytes in measurementbytes_generator:
        measurement = decode_measurement(measurementbytes)
        timestamp = measurement["timestamp"]

        if not currtimestamp:
            currtimestamp = timestamp

        if currtimestamp - timestamp < datetime.timedelta(seconds=interval):
            measurements.append(measurement)
            continue
        else:
            currtimestamp = timestamp
            yield measurements
            measurements = [measurement]


def groups_to_average(fieldname, measurement_generator):
    for measurements in measurement_generator:
        temperatures = [measurement[fieldname] for measurement in measurements]
        yield measurements[0]["timestamp"], round(util.avg(temperatures), 2)
