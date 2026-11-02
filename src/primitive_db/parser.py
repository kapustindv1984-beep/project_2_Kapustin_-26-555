import re
from typing import Dict, List, Any, Optional, Tuple


def parse_create_table(args: List[str]) -> Tuple[str, Dict[str, str]]:
    if len(args) < 3:
        raise ValueError("Недостаточно аргументов. Формат: create_table <имя> <col:type> ...")

    table_name = args[1]
    schema_str = args[2:]

    schema = {}
    for part in schema_str:
        if ":" not in part:
            raise ValueError(f"Неверный формат колонки '{part}'. Ожидалось col:type")
        col, dtype = part.split(":", 1)
        schema[col] = dtype

    return table_name, schema


def parse_insert(args: List[str]) -> Tuple[str, Dict[str, Any]]:
    if len(args) < 4 or args[1] != "into":
        raise ValueError("Неверный синтаксис INSERT. Формат: insert into <table> key:value ...")

    table_name = args[2]
    pairs = args[3:]

    if not pairs:
        raise ValueError("Нет данных для вставки. Формат: insert into <table> key:value ...")

    kv_pairs = {}
    pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$'

    for p in pairs:
        m = re.match(pattern, p)
        if not m:
            raise ValueError(f"Неверная пара '{p}'. Ожидалось key:value")
        key, raw_val = m.group(1), m.group(2).strip()
        val = _parse_value(raw_val)
        kv_pairs[key] = val

    return table_name, kv_pairs


def _parse_value(raw: str) -> Any:
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]

    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False

    try:
        return int(raw)
    except ValueError:
        pass

    return raw


def parse_select(args: List[str]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Неверный синтаксис SELECT. Формат: select from <table> [where key:value]")

    table_name = args[2]
    where_clause = None

    if len(args) >= 5 and args[3] == "where":
        where_part = args[4]
        if ":" not in where_part:
            raise ValueError("Неверный формат условия WHERE. Ожидалось key:value")
        k, v_raw = where_part.split(":", 1)
        v = _parse_value(v_raw)
        where_clause = {k: v}

    return table_name, where_clause


def parse_update(args: List[str]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    if len(args) < 6 or args[2] != "set":
        raise ValueError("Неверный синтаксис UPDATE. Формат: update <table> set key:value ... where key:value")

    table_name = args[1]

    try:
        where_idx = args.index("where")
    except ValueError:
        raise ValueError("Отсутствует условие WHERE в UPDATE")

    set_parts = args[3:where_idx]
    where_part = args[where_idx + 1]

    if ":" not in where_part:
        raise ValueError("Неверный формат WHERE. Ожидалось key:value")
    k, v_raw = where_part.split(":", 1)
    where_val = _parse_value(v_raw)
    where_values = {k: where_val}

    set_values = {}
    for p in set_parts:
        if ":" not in p:
            raise ValueError(f"Неверная пара в SET: '{p}'")
        k, v_raw = p.split(":", 1)
        set_values[k] = _parse_value(v_raw)

    return table_name, set_values, where_values


def parse_delete(args: List[str]) -> Tuple[str, Dict[str, Any]]:
    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        raise ValueError("Неверный синтаксис DELETE. Формат: delete from <table> where key:value")

    table_name = args[2]
    where_part = args[4]

    if ":" not in where_part:
        raise ValueError("Неверный формат WHERE. Ожидалось key:value")
    k, v_raw = where_part.split(":", 1)
    where_val = _parse_value(v_raw)

    return table_name, {k: where_val}