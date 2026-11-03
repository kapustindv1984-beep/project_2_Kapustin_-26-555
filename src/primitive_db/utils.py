import json
import os
from pathlib import Path
from .constants import DATA_DIR, META_FILE

def _ensure_dirs():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

def ensure_data_dir():
    _ensure_dirs()

def load_metadata():
    _ensure_dirs()
    path = Path(DATA_DIR) / META_FILE
    
    if not path.exists():
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Файл метаданных поврежден (JSON Error): {e}")
    except IOError as e:
        raise IOError(f"Не удалось прочитать файл метаданных: {e}")

def save_metadata(metadata):
    _ensure_dirs()
    path = Path(DATA_DIR) / META_FILE
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    except IOError as e:
        raise IOError(f"Не удалось сохранить метаданные: {e}")

def load_table_data(table_name: str):
    path = os.path.join(DATA_DIR, f"{table_name}.json")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл данных для таблицы '{table_name}' не найден: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Файл данных '{table_name}.json' пуст или повреждён.")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Файл данных '{table_name}.json' поврежден (JSON Error): {e}")

def save_table_data(table_name, rows):
    os.makedirs(DATA_DIR, exist_ok=True)
    _ensure_dirs()
    path = Path(DATA_DIR) / f"{table_name}.json"
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
    except IOError as e:
        raise IOError(f"Не удалось сохранить данные таблицы '{table_name}': {e}")