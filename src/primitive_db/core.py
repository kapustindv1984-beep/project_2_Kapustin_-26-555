from typing import Any, Dict, List, Optional
from .constants import VALID_TYPES
from .utils import load_metadata, save_metadata, load_table_data, save_table_data

def create_table(table_name: str, schema: Dict[str, str]) -> bool:
    if not all(t in VALID_TYPES for t in schema.values()):
        return False
    
    metadata = load_metadata()
    if table_name in metadata:
        return False
    
    metadata[table_name] = {"schema": schema, "indexes": []}
    return save_metadata(metadata)

def insert_row(table_name: str, row: Dict[str, Any]) -> bool:
    metadata = load_metadata()
    if table_name not in metadata:
        return False
    
    schema = metadata[table_name]["schema"]
    for col, val in row.items():
        if col not in schema:
            return False
        col_type = schema[col]
        if col_type == "int" and not isinstance(val, int):
            return False
        if col_type == "str" and not isinstance(val, str):
            return False
        if col_type == "bool" and not isinstance(val, bool):
            return False
    
    data = load_table_data(table_name)
    data.append(row)
    return save_table_data(table_name, data)

def select_rows(table_name: str, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    metadata = load_metadata()
    if table_name not in metadata:
        return 
    
    data = load_table_data(table_name)
    if not where:
        return data
    
    col, val = next(iter(where.items()))
    return [row for row in data if row.get(col) == val]

def update_rows(table_name: str, set_values: Dict[str, Any], where: Dict[str, Any]) -> int:
    metadata = load_metadata()
    if table_name not in metadata:
        return 0
    
    schema = metadata[table_name]["schema"]
    for col, val in set_values.items():
        if col not in schema:
            return 0
        col_type = schema[col]
        if col_type == "int" and not isinstance(val, int):
            return 0
        if col_type == "str" and not isinstance(val, str):
            return 0
        if col_type == "bool" and not isinstance(val, bool):
            return 0
    
    data = load_table_data(table_name)
    col, val = next(iter(where.items()))
    updated_count = 0
    for row in data:
        if row.get(col) == val:
            row.update(set_values)
            updated_count += 1
    
    if updated_count > 0:
        save_table_data(table_name, data)
    
    return updated_count

def delete_rows(table_name: str, where: Dict[str, Any]) -> int:
    metadata = load_metadata()
    if table_name not in metadata:
        return 0
    
    data = load_table_data(table_name)
    col, val = next(iter(where.items()))
    original_len = len(data)
    data = [row for row in data if row.get(col) != val]
    
    if len(data) < original_len:
        save_table_data(table_name, data)
    
    return original_len - len(data)