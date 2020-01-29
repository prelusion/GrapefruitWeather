import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
REPO_DIR = os.path.dirname(ROOT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
MEASUREMENTS_DIR = os.environ.get("MEASUREMENTS_DB", os.path.join(DATA_DIR, "measurements"))
TRACK_CACHE_DIR = os.path.join(DATA_DIR, "track_distance_cache")
DEFAULT_LIMIT = 50
