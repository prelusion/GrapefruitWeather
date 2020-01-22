import datetime
import math
import os
import timeit
from collections import OrderedDict

from app import const

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


def iterate_dataset_left(data, fieldname):
    """ Each iteration the value of the given fieldname is yielded. """
    i = len(data)
    while i > 0:
        measurementaddr = (i - MEASUREMENT_BYTE_COUNT)
        yield data[measurementaddr:measurementaddr + MEASUREMENT_BYTE_COUNT]
        i -= MEASUREMENT_BYTE_COUNT


def filter_measurements_by_field(data, fieldname, value):
    fieldaddr = PROTOCOL_FORMAT_BS[fieldname]
    field_bc = PROTOCOL_FORMAT_BC[fieldname]

    for measurementbytes in iterate_dataset_left(data, "station_id"):
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        decoded = decode_field(fieldname, bytevalue)

        if decoded == value:
            yield measurementbytes


def filter_measurements_by_timestamp(data, station_id, dt1, dt2):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]

    for measurementbytes in filter_measurements_by_field(data, "station_id", station_id):
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if dt1 < timestamp <= dt2:
            yield decode_measurement(bytevalue)
        elif timestamp < dt1:
            break


def filter_most_recent_measurements(data, station_id, seconds):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]

    first = None

    for measurementbytes in filter_measurements_by_field(data, "station_id", station_id):
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if not first:
            first = timestamp

        if timestamp < first - datetime.timedelta(seconds=seconds):
            break

        yield decode_measurement(measurementbytes)


if __name__ == "__main__":
    dataread = read_test_file()

    print(timeit.timeit(
        "print(len(list(filter_most_recent_measurements(dataread, 743700, 120))))",
        number=1,
        globals=globals()
    ))

    # test1_dt1 = datetime.datetime(2020, 1, 21, 14, 56, 38)
    # test1_dt2 = datetime.datetime(2020, 1, 21, 14, 57, 38)
    #
    # print(timeit.timeit(
    #     "print(len(list(filter_measurements_by_timestamp(dataread, 743700, test1_dt1, test1_dt2))))",
    #     number=1,
    #     globals=globals()
    # ))
    #
    # test2_dt1 = datetime.datetime(2020, 1, 21, 14, 59, 30)
    # test2_dt2 = datetime.datetime(2020, 1, 21, 15, 1, 30)
    #
    # print(timeit.timeit(
    #     "print(len(list(filter_measurements_by_timestamp(dataread, 743700, test2_dt1, test2_dt2))))",
    #     number=1,
    #     globals=globals()
    # ))
