from typing import Any, Dict, List, Optional
from .constants import VALID_TYPES
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
import os


def create_table(table_name: str, schema: Dict[str, str]) -> str:
    for col, dtype in schema.items():
        if dtype not in VALID_TYPES:
            return f"Ошибка: тип '{dtype}' не поддерживается. Допустимы: {VALID_TYPES}"
    metadata = load_metadata()
    if table_name in metadata:
        return f"Таблица '{table_name}' уже существует."
    if "ID" not in schema:
        schema = {"ID": "int", **schema}
    else:
        if schema["ID"] != "int":
            return "Ошибка: столбец 'ID' должен быть типа 'int'."
    metadata[table_name] = {
        "schema": schema,
        "indexes": [],
        "next_id": 1
    }
    save_metadata(metadata)
    return f"Таблица '{table_name}' создана."


def insert_row(table_name: str, values: List[Any]) -> str:
    metadata = load_metadata()
    if table_name not in metadata:
        return f"Ошибка: таблица '{table_name}' не найдена."
    table_info = metadata[table_name]
    schema = table_info["schema"]
    cols = list(schema.keys())
    data_cols = [c for c in cols if c != "ID"]
    if len(values) != len(data_cols):
        return f"Ошибка: ожидается {len(data_cols)} значений (без ID), получено {len(values)}."
    next_id = table_info.get("next_id", 1)
    table_info["next_id"] = next_id + 1
    save_metadata(metadata)
    rows = load_table_data(table_name)
    if rows is None:
        rows = []
    for i, col in enumerate(data_cols):
        dtype = schema[col]
        val = values[i]
        if dtype == "int" and not isinstance(val, int):
            return f"Ошибка: для колонки '{col}' требуется тип 'int', получено '{val}'."
        if dtype == "str" and not isinstance(val, str):
            return f"Ошибка: для колонки '{col}' требуется тип 'str', получено '{val}'."
        if dtype == "bool" and not isinstance(val, bool):
            return f"Ошибка: для колонки '{col}' требуется тип 'bool', получено '{val}'."
    new_row = [next_id] + values
    rows.append(new_row)
    save_table_data(table_name, rows)
    return f"Запись с ID={next_id} успешно добавлена в таблицу \"{table_name}\"."


def select_rows(table_name: str, where_clause: Optional[Dict[str, Any]]) -> List[List[Any]]:
    rows = load_table_data(table_name)
    if rows is None:
        return []
    if not where_clause:
        return rows
    filtered = []
    col, expected_val = next(iter(where_clause.items()))
    metadata = load_metadata()
    schema = metadata[table_name]["schema"]
    cols = list(schema.keys())
    data_cols = [c for c in cols if c != "ID"]
    try:
        idx = data_cols.index(col) + 1
    except ValueError:
        return []
    for row in rows:
        if row[idx] == expected_val:
            filtered.append(row)
    return filtered


def update_rows(table_name: str, set_clause: Dict[str, Any], where_clause: Dict[str, Any]) -> str:
    rows = load_table_data(table_name)
    if rows is None:
        return "Ошибка: таблица не найдена."
    metadata = load_metadata()
    schema = metadata[table_name]["schema"]
    cols = list(schema.keys())
    data_cols = [c for c in cols if c != "ID"]
    updated_count = 0
    set_col, set_val = next(iter(set_clause.items()))
    where_col, where_val = next(iter(where_clause.items()))
    try:
        set_idx = data_cols.index(set_col) + 1
        where_idx = data_cols.index(where_col) + 1
    except ValueError as e:
        return f"Ошибка: колонка не найдена — {e}"
    for row in rows:
        if row[where_idx] == where_val:
            row[set_idx] = set_val
            updated_count += 1
    save_table_data(table_name, rows)
    return f"Обновлено записей: {updated_count}"


def delete_rows(table_name: str, where_clause: Dict[str, Any]) -> str:
    rows = load_table_data(table_name)
    if rows is None:
        return "Ошибка: таблица не найдена."
    metadata = load_metadata()
    schema = metadata[table_name]["schema"]
    cols = list(schema.keys())
    data_cols = [c for c in cols if c != "ID"]
    where_col, where_val = next(iter(where_clause.items()))
    try:
        idx = data_cols.index(where_col) + 1
    except ValueError:
        return "Ошибка: колонка в условии WHERE не найдена."
    initial_len = len(rows)
    filtered = [row for row in rows if row[idx] != where_val]
    deleted_count = initial_len - len(filtered)
    save_table_data(table_name, filtered)
    return f"Удалено записей: {deleted_count}"


def drop_table(table_name: str) -> str:
    metadata = load_metadata()
    if table_name not in metadata:
        return f"Ошибка: таблица '{table_name}' не найдена."
    del metadata[table_name]
    save_metadata(metadata)
    data_path = f"data/{table_name}.json"
    if os.path.exists(data_path):
        os.remove(data_path)
    return f"Таблица '{table_name}' удалена."