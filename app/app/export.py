import time
import os
import json
from datetime import datetime
from app import db
from app import fileaccess
from app import const


def create_export(stations, fields, hours, timezone_id=None):
    tstart = time.time()
    # measurements = db.get_all_measurements(stations, fields, hours)
    measurements = [{"test": "test"}]
    duration = time.time() - tstart

    if timezone_id:
        timezone = db.get_timezone_by_timezone_id(timezone_id)
        #  TODO timezone conversion

    os.makedirs(const.EXPORTS_DIR, exist_ok=True)

    export_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    filepath = os.path.join(const.EXPORTS_DIR, export_id)

    with open(filepath, "w") as f:
        json.dump(measurements, f)
