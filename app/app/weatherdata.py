"""
Max chunksize for 8 GB RAM on Dell Inspiron 5570 with other programs running:
187,5 MB    -> Memory error
157,5 MB    -> Memory Error
150 MB      -> Fine
"""
import datetime
import math
import os
import re
from collections import OrderedDict

from app import const
from app import util

MAX_CHUNKSIZE = 100000000  # 100 MB

WSMC_EXTENSION = ".wsmc"
WSAMC_EXTENSION = ".wsamc"

# Byte count for each field within a measurement
WSMC_PROTOCOL_FORMAT_BC = OrderedDict({
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
WSMC_PROTOCOL_FORMAT_BS = OrderedDict({
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

WSMC_MEASUREMENT_BYTE_COUNT = sum(WSMC_PROTOCOL_FORMAT_BC.values())

# Byte count for each field within an average measurement
WSAMC_PROTOCOL_FORMAT_BC = OrderedDict({
    "station_id": 3,
    "timestamp": 4,
    "count": 2,
    "temperature": 3,
    "dew_point": 3,
    "air_pressure": 3,
    "sea_air_pressure": 3,
    "visibility": 2,
    "air_speed": 2,
    "rainfall": 3,
    "snowfall": 3,
    "cloud_pct": 2,
    "wind_direction": 2,
})

# Starting byte for each field within an average measurement
WSAMC_PROTOCOL_FORMAT_BS = OrderedDict({
    "station_id": 0,
    "timestamp": 3,
    "count": 7,
    "temperature": 9,
    "dew_point": 12,
    "air_pressure": 15,
    "sea_air_pressure": 18,
    "visibility": 21,
    "air_speed": 23,
    "rainfall": 25,
    "snowfall": 28,
    "cloud_pct": 31,
    "wind_direction": 33,
})

WSAMC_MEASUREMENT_BYTE_COUNT = sum(WSAMC_PROTOCOL_FORMAT_BC.values())


def determine_chunksize(prefsize=500000):
    chunks = math.trunc(prefsize / WSMC_MEASUREMENT_BYTE_COUNT)
    return chunks * WSMC_MEASUREMENT_BYTE_COUNT


def get_files(datadir, extension):
    files = os.listdir(datadir)
    files = list(filter(lambda file: file.endswith(extension), files))
    files.sort(key=lambda name: int(re.sub('\D', '', name)))
    return list(((name, os.path.join(datadir, name)) for name in files if extension in name))


def load_data_per_file(datadir, offset, extension):
    """ Loads wsmc data from the file system.
    Data is loaded backwards, which implies that the newest data is loaded first.
    Data is loaded per file, so data from multiple files can not be loaded into memory
    simultaneously. This means that the file size should be optimized to the maximum chunk size.
    Based on most recent benchmarks, loading data per file performs better
    than loading data per chunk.
    :param offset: amount of chunks skipped when loading into memory
    :return: data in bytes
    """
    files = get_files(datadir, extension)

    index = (len(files) - 1) - offset
    if index < 0:
        return []

    filename, filepath = files[index]

    size = os.path.getsize(filepath)
    if size > MAX_CHUNKSIZE:
        raise RuntimeError(
            f"Unable to load file with a size greater than max chunk size: {MAX_CHUNKSIZE}")

    return read_file(filepath)


def load_data_per_chunk(chunksize, offset):
    """ DEPRECATED: Please use load_data_per_file instead.
    Based on most recent benchmarks, loading data per file performs better
    than loading data per chunk.
    Loads wsmc data from the file system.
    Data is loaded backwards, which implies that the newest data is loaded first.
    :param offset: amount of chunks skipped when loading into memory
    :param chunksize: preferred amount of bytes loaded into memory
    :return: data in bytes
    """
    return _load_data_per_chunk(determine_chunksize(chunksize), offset)


def _load_data_per_chunk(chunksize, offset):
    skipbytes = offset * chunksize
    spaceleft = chunksize
    files = get_files()
    totaldata = []

    index = len(files) - 1
    if index < 0:
        return []

    while index >= 0 and spaceleft > WSMC_MEASUREMENT_BYTE_COUNT:
        filename, filepath = files[index]
        size = os.path.getsize(filepath)

        if skipbytes > size:
            skipbytes -= size
        else:
            data = read_file(filepath, bytecount=spaceleft, skipbytes=skipbytes)
            skipbytes = 0
            spaceleft -= len(data)
            totaldata.extend(data)

        index -= 1

    return totaldata


def read_file(filepath, bytecount=None, skipbytes=None):
    """ Reads a .wsmc file into memory.
    This function also checks that the file does not include corrupt measurements.
    :param filepath: path to .wsmc file
    :param bytecount: amount of bytes to load into memory, by default loads whole file
    :param skipbytes: amount of bytes skipped from beginning of file
    :return: data in bytes
    """
    with open(filepath, "rb") as f:
        if skipbytes:
            f.seek(skipbytes, 0)
        if bytecount:
            data = f.read(bytecount)
        else:
            data = f.read()

    if len(data) % WSMC_MEASUREMENT_BYTE_COUNT != 0:
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


def decode_measurement(bindata, skipfields=None):
    measurement = OrderedDict()
    i = 0

    for field, bytecount in WSMC_PROTOCOL_FORMAT_BC.items():
        if skipfields and field in skipfields:
            continue
        measurement[field] = decode_field(field, bindata[i:i + bytecount])
        i += bytecount

    return measurement


def iterate_dataset_left(data):
    """ Each iteration the value of the given fieldname is yielded. """
    i = len(data)
    while i > 0:
        measurementaddr = (i - WSMC_MEASUREMENT_BYTE_COUNT)
        yield data[measurementaddr:measurementaddr + WSMC_MEASUREMENT_BYTE_COUNT]
        i -= WSMC_MEASUREMENT_BYTE_COUNT


def filter_by_field(measurementbytes_generator, fieldname, values):
    fieldaddr = WSMC_PROTOCOL_FORMAT_BS[fieldname]
    field_bc = WSMC_PROTOCOL_FORMAT_BC[fieldname]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        decoded = decode_field(fieldname, bytevalue)

        if decoded in values:
            yield measurementbytes


def filter_by_timestamp(measurementbytes_generator, dt1, dt2):
    fieldaddr = WSMC_PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = WSMC_PROTOCOL_FORMAT_BC["timestamp"]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if dt1 < timestamp <= dt2:
            yield decode_measurement(bytevalue)
        elif timestamp < dt1:
            break


def filter_most_recent(measurementbytes_generator, seconds):
    fieldaddr = WSMC_PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = WSMC_PROTOCOL_FORMAT_BC["timestamp"]
    first = None

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if not first:
            first = timestamp

        if timestamp < first - datetime.timedelta(seconds=seconds):
            break

        yield timestamp, measurementbytes


def group_by_timestamp(measurementbytes_generator, interval):
    measurements = []
    currtimestamp = None

    for timestamp, measurementbytes in measurementbytes_generator:
        measurement = decode_measurement(measurementbytes, skipfields=["timestamp"])
        measurement["timestamp"] = timestamp

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


def decode_measurement_fields(measurementbytes_generator, fields):
    for timestamp, measurementbytes in measurementbytes_generator:
        measurement = OrderedDict()
        measurement["timestamp"] = timestamp
        for field in fields:
            if field == "timestamp":
                continue
            fieldaddr = WSMC_PROTOCOL_FORMAT_BS[field]
            field_bc = WSMC_PROTOCOL_FORMAT_BS[field]
            bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
            measurement[field] = decode_field(field, bytevalue)
        yield measurement
