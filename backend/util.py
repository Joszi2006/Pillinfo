import json
import os

# Path to your existing cached labels file
CACHED_FILE = "data/cached_labels.json"

# Ensure the file exists
if not os.path.exists(CACHED_FILE):
    with open(CACHED_FILE, "w") as f:
        json.dump({}, f)

def load_cached_labels():
    if not os.path.exists(CACHED_FILE):
        return {}
    with open(CACHED_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # return empty dict if file is empty or invalid


def save_cached_labels(labels_dict):
    with open(CACHED_FILE, "w") as f:
        json.dump(labels_dict, f, indent=2)