from bisect import bisect_left
from datetime import timedelta

from flask import jsonify


def avg(lst):
    return sum(lst) / len(lst)


def split_by_interval(array, interval: int):
    """ This function splits a sorted timestamped array into averages for each interval.

        :param array: array of objects containing a timestamp and a value property defined by value_field
        :param value_field: the field name in the array elements that contains the value to be averaged
        :param interval: interval in seconds, all measurements between each interval are averaged
    """

    prev_timestamp = array[0]["timestamp"]
    values = 0
    count = 0
    averages = []

    for el in array:
        if el["timestamp"] - prev_timestamp >= timedelta(interval):
            prev_timestamp = el["timestamp"]
            avg = values / count
            averages.append(avg)
            values = count = 0
        else:
            values += el["value"]
            count += 1


def binary_search(array, value):
    i = bisect_left(array, value)
    if i != len(array) and array[i] == value:
        return i
    else:
        return -1


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


def http_format_error(message):
    return jsonify({"error": message})


def http_format_data(data, params=None):
    response = {"data": data}

    for param, value in params.items():
        response[param] = value

    return jsonify(response)
