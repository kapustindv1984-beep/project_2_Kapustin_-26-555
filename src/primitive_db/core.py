from pathlib import Path
from typing import Any

from .constants import DATA_DIR, VALID_TYPES
from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

_select_cache = create_cacher()
_table_version: dict[str, int] = {}


def _bump_version(table_name: str) -> None:
    _table_version[table_name] = _table_version.get(table_name, 0) + 1

def _get_table_info(table_name: str):
    metadata = load_metadata()
    if not metadata:
        return None, None
    
    if table_name not in metadata:
        return None, None
    
    table_meta = metadata[table_name]
    schema = table_meta.get("schema", {})
    col_to_index = {col_name: idx for idx, col_name in enumerate(schema.keys())}
    
    return schema, col_to_index

@handle_db_errors
@log_time
def create_table(table_name: str, schema: dict[str, str]) -> str:
    for col, dtype in schema.items():
        if dtype not in VALID_TYPES:
            raise TypeError(f"Тип '{dtype}' для колонки '{col}' не поддерживается. Допустимы: {VALID_TYPES}")

    metadata = load_metadata()
    if not metadata:
        metadata = {}

    if table_name in metadata:
        raise ValueError(f"Ошибка: таблица '{table_name}' уже существует.")

    if "ID" not in schema:
        schema = {"ID": "int", **schema}
    else:
        if schema["ID"] != "int":
            raise ValueError("Ошибка: столбец 'ID' должен быть типа 'int'.")

    metadata[table_name] = {
        "schema": schema,
        "indexes": None,
        "next_id": 1
    }

    save_metadata(metadata)
    
    save_table_data(table_name, [])
    _table_version[table_name] = 0

    return f"Таблица '{table_name}' успешно создана."

@handle_db_errors
@log_time
def insert_row(table_name, values):
    metadata = load_metadata()
    if not metadata or table_name not in metadata:
        raise KeyError(f"Ошибка: таблица '{table_name}' не найдена.")

    table_meta = metadata[table_name]
    schema = table_meta.get("schema", {})
    
    all_columns = list(schema.keys())
    if not all_columns:
        raise ValueError("Ошибка: схема таблицы пуста.")
    
    data_columns = all_columns[1:]

    if len(values) != len(data_columns):
        expected = len(data_columns)
        raise ValueError(f"Ошибка: ожидается {expected} значений, получено {len(values)}.")

    type_map = {
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
    }

    for i, col_name in enumerate(data_columns):
        expected_type = schema[col_name]
        val = values[i]
        
        if expected_type not in type_map:
            raise ValueError(f"Ошибка: неизвестный тип '{expected_type}' для колонки '{col_name}'.")
        
        target_cls = type_map[expected_type]
        
        if not isinstance(val, target_cls):
            if expected_type == "bool":
                raise ValueError(f"Ошибка: для колонки '{col_name}' требуется тип 'bool', получено '{type(val).__name__}'.")
            raise ValueError(f"Ошибка: тип значения для колонки '{col_name}' должен быть '{expected_type}', получено '{type(val).__name__}'.")  # noqa: TRY004

    data = load_table_data(table_name)
    if data is None:
        data = []

    next_id = table_meta.get("next_id", 1)
    table_meta["next_id"] = next_id + 1
    
    save_metadata(metadata)

    new_row = [next_id] + list(values)
    data.append(new_row)

    save_table_data(table_name, data)
    _bump_version(table_name)

    return f"Успешно: вставлена 1 запись. Новый ID: {next_id}"

def _matches_where_clause(row, col_to_index, where_clause):
    for col_name, target_val in where_clause.items():
        if col_name not in col_to_index:
            return False
        idx = col_to_index[col_name]
        if idx >= len(row):
            return False
        actual_val = row[idx]
        if isinstance(actual_val, str) and isinstance(target_val, str):
            def norm(s):
                return s.strip().lower().replace('ё', 'е')
            if norm(actual_val) != norm(target_val):
                return False
        elif actual_val != target_val:
            return False
    return True


@handle_db_errors
@log_time
def select_rows(table_name: str, where_clause: dict | None = None):
    key = f"{table_name}:{_table_version.get(table_name, 0)}:{where_clause!s}"

    def fetch_data():
        schema, col_to_index = _get_table_info(table_name)
        if not schema:
            raise KeyError(f"Ошибка: таблица '{table_name}' не найдена.")

        data = load_table_data(table_name)
        if not where_clause:
            return data

        return [
            row for row in data
            if isinstance(row, list) and _matches_where_clause(row, col_to_index, where_clause)
        ]

    return _select_cache(key, fetch_data)

@handle_db_errors
@log_time
def update_rows(table_name: str, set_clause: dict[str, Any], where_clause: dict[str, Any]) -> str:
    schema, col_to_index = _get_table_info(table_name)
    
    if schema is None:
        raise KeyError(f"Ошибка: таблица '{table_name}' не найдена.")

    for col in set_clause:
        if col not in col_to_index:
            raise KeyError(f"Ошибка: колонка '{col}' не найдена в таблице '{table_name}'.")
    
    data = load_table_data(table_name)
    if data is None:
         raise ValueError(f"Данные для таблицы '{table_name}' не загружены.")

    updated_count = 0
    
    for row in data:
        if not isinstance(row, list):
            continue
        if _matches_where_clause(row, col_to_index, where_clause):
            for col, new_val in set_clause.items():
                idx = col_to_index[col]
                if idx < len(row):
                    row[idx] = new_val
            updated_count += 1

    if updated_count > 0:
        save_table_data(table_name, data)
        _bump_version(table_name)

    return f"Обновлено записей: {updated_count}"

@handle_db_errors
@log_time
def delete_rows(table_name: str, where_clause: dict[str, Any]) -> str:
    schema, col_to_index = _get_table_info(table_name)

    if schema is None:
        raise KeyError(f"Ошибка: таблица '{table_name}' не найдена.")

    data = load_table_data(table_name)
    if data is None:
        raise ValueError(f"Данные для таблицы '{table_name}' не загружены.")

    # Сначала проверяем целостность всех строк (чтобы не портить данные)
    for i, row in enumerate(data):
        if not isinstance(row, list):
            raise ValueError(f"Ошибка: строка {i} не является списком (повреждённые данные).")  # noqa: TRY004

    initial_len = len(data)
    # Оставляем только строки, которые НЕ совпадают с условием where
    filtered = [
        row for row in data
        if not _matches_where_clause(row, col_to_index, where_clause)
    ]
    deleted_count = initial_len - len(filtered)

    if deleted_count > 0:
        save_table_data(table_name, filtered)
        _bump_version(table_name)

    return f"Удалено записей: {deleted_count}"

@confirm_action("удаление таблицы")
@handle_db_errors
@log_time
def drop_table(table_name: str) -> str:
    metadata = load_metadata()
    if not metadata or table_name not in metadata:
        raise KeyError(f"Ошибка: таблица '{table_name}' не найдена.")
    
    del metadata[table_name]
    save_metadata(metadata)
    
    data_path = Path(DATA_DIR) / f"{table_name}.json"
    if data_path.exists():
        try:
            data_path.unlink()
        except OSError as e:
            raise OSError(f"Не удалось удалить файл данных '{data_path}': {e}")
        
    _bump_version(table_name)
    return f"Таблица '{table_name}' удалена."
