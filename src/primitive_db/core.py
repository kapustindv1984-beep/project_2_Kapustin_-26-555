from typing import Any, Dict, List
from .constants import VALID_TYPES
from .utils import load_metadata, save_metadata, load_table_data, save_table_data


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


def insert_row(table_name: str, values_dict: Dict[str, Any]) -> str:
    metadata = load_metadata()
    if table_name not in metadata:
        return f"Ошибка: таблица '{table_name}' не найдена."

    table_info = metadata[table_name]
    schema = table_info["schema"]

    if "ID" not in schema:
        return "Ошибка: в схеме таблицы отсутствует столбец 'ID'."

    next_id = table_info.get("next_id", 1)
    table_info["next_id"] = next_id + 1
    save_metadata(metadata)

    rows = load_table_data(table_name)
    if rows is None:
        rows = []

    cols_order = list(schema.keys())

    ordered_values = []
    for col in cols_order:
        if col == "ID":
            continue
        if col not in values_dict:
            return f"Ошибка: не указано значение для колонки '{col}'."
        ordered_values.append(values_dict[col])

    new_row = [next_id] + ordered_values
    rows.append(new_row)
    save_table_data(table_name, rows)

    return f"Запись добавлена (ID={next_id})."


def select_rows(table_name: str, where_clause: Optional[Dict[str, Any]] = None) -> Optional[List[Any]]:
    rows = load_table_data(table_name)
    if rows is None:
        return None

    if not where_clause:
        return rows

    col, expected_val = next(iter(where_clause.items()))
    filtered = [row for row in rows if len(row) > 0 and row[0] == expected_val]
    return filtered


def update_rows(table_name: str, set_values: Dict[str, Any], where: Dict[str, Any]) -> str:
    metadata = load_metadata()
    if table_name not in metadata:
        return f"Ошибка: таблица '{table_name}' не найдена."

    schema = metadata[table_name]["schema"]
    cols_order = list(schema.keys())

    for col, val in set_values.items():
        if col not in schema:
            return f"Ошибка: колонка '{col}' не существует."
        col_type = schema[col]
        if col_type == "int" and not isinstance(val, int):
            return f"Ошибка: для колонки '{col}' требуется тип 'int'."
        if col_type == "str" and not isinstance(val, str):
            return f"Ошибка: для колонки '{col}' требуется тип 'str'."
        if col_type == "bool" and not isinstance(val, bool):
            return f"Ошибка: для колонки '{col}' требуется тип 'bool'."

    data = load_table_data(table_name)
    if data is None:
        data = []

    where_col = next(iter(where.keys()))
    where_val = where[where_col]
    where_idx = cols_order.index(where_col) if where_col in cols_order else 0

    updated_count = 0
    for row in data:
        if len(row) <= where_idx:
            continue
        if row[where_idx] == where_val:
            for c, v in set_values.items():
                c_idx = cols_order.index(c) if c in cols_order else -1
                if 0 <= c_idx < len(row):
                    row[c_idx] = v
            updated_count += 1

    if updated_count > 0:
        save_table_data(table_name, data)

    return f"Обновлено строк: {updated_count}"


def delete_rows(table_name: str, where: Dict[str, Any]) -> str:
    metadata = load_metadata()
    if table_name not in metadata:
        return f"Ошибка: таблица '{table_name}' не найдена."

    data = load_table_data(table_name)
    if data is None:
        data = []

    where_col = next(iter(where.keys()))
    where_val = where[where_col]

    cols_order = list(metadata[table_name]["schema"].keys())
    where_idx = cols_order.index(where_col) if where_col in cols_order else 0

    original_len = len(data)
    filtered_data = [
        row for row in data
        if not (len(row) > where_idx and row[where_idx] == where_val)
    ]

    deleted_count = original_len - len(filtered_data)
    if deleted_count > 0:
        save_table_data(table_name, filtered_data)

    return f"Удалено строк: {deleted_count}"


def drop_table(table_name: str) -> str:
    import os
    metadata = load_metadata()

    if table_name not in metadata:
        return f"Ошибка: Таблица '{table_name}' не существует."

    del metadata[table_name]
    save_metadata(metadata)

    data_dir = "data"
    file_path = os.path.join(data_dir, f"{table_name}.json")
    if os.path.exists(file_path):
        os.remove(file_path)

    return f"Таблица '{table_name}' успешно удалена."