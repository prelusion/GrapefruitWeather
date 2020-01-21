import os


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
REPO_DIR = os.path.dirname(ROOT_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
MEASUREMENTS_DIR = os.path.join(DATA_DIR, "measurements")
