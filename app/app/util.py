from datetime import datetime, timedelta
from typing import TypedDict, List


def avg(lst):
    return sum(lst) / len(lst)


class SortedTimestampedArray(TypedDict):
    timestamp: datetime
    value: int


def split_by_interval(array: List[SortedTimestampedArray], interval: int):
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
