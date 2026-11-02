import re
from typing import Dict, List, Any, Optional, Tuple


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
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


def parse_insert(args: List[str]) -> Tuple[str, List[Any]]:
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        raise ValueError("Неверный синтаксис INSERT. Формат: insert into <таблица> values (val1, val2, ...)")
    table_name = args[2]
    values_str = args[4]
    if not values_str.startswith("(") or not values_str.endswith(")"):
        raise ValueError("Значения должны быть в скобках: values (...)")
    values_content = values_str[1:-1].strip()
    if not values_content:
        return table_name, []
    raw_values = [v.strip() for v in values_content.split(",")]
    parsed_values = []
    for v in raw_values:
        if not v:
            continue
        parsed_values.append(_parse_value(v))
    return table_name, parsed_values


def _parse_condition(cond_str: str) -> Dict[str, Any]:
    match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$', cond_str.strip())
    if not match:
        raise ValueError(f"Неверный формат условия: '{cond_str}'. Ожидалось col = value")
    col, raw_val = match.group(1), match.group(2).strip()
    val = _parse_value(raw_val)
    return {col: val}


def parse_select(args: List[str]) -> Tuple[str, Optional[Dict[str, Any]]]:
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Неверный синтаксис SELECT. Формат: select from <таблица> [where col = value]")
    table_name = args[2]
    where_clause = None
    if len(args) >= 5 and args[3] == "where":
        where_clause = _parse_condition(args[4])
    return table_name, where_clause


def parse_update(args: List[str]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    if len(args) < 6 or args[2] != "set" or "where" not in args:
        raise ValueError("Неверный синтаксис UPDATE. Формат: update <таблица> set col = val where col = val")
    table_name = args[1]
    try:
        where_idx = args.index("where")
    except ValueError:
        raise ValueError("Отсутствует условие WHERE в UPDATE")
    set_part = args[3:where_idx]
    where_part = args[where_idx + 1]
    if len(set_part) != 1:
        raise ValueError("В SET поддерживаются только одиночные присваивания по ТЗ: set col = val")
    set_values = _parse_condition(set_part[0])
    where_values = _parse_condition(where_part)
    return table_name, set_values, where_values


def parse_delete(args: List[str]) -> Tuple[str, Dict[str, Any]]:
    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        raise ValueError("Неверный синтаксис DELETE. Формат: delete from <таблица> where col = val")
    table_name = args[2]
    where_values = _parse_condition(args[4])
    return table_name, where_values