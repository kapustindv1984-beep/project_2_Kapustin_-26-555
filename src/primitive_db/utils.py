import json
import os
from pathlib import Path
from .constants import META_FILE, DATA_DIR

def _ensure_dirs():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

def load_metadata():
    _ensure_dirs()
    path = Path(DATA_DIR) / META_FILE
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_metadata(metadata):
    _ensure_dirs()
    path = Path(DATA_DIR) / META_FILE
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def load_table_data(table_name):
    _ensure_dirs()
    path = Path(DATA_DIR) / f"{table_name}.json"
    if not path.exists():
        return 
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_table_data(table_name, rows):
    _ensure_dirs()
    path = Path(DATA_DIR) / f"{table_name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)