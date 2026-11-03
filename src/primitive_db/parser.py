import re
from typing import Any


def _parse_value(raw: str) -> Any:
    # 1. Убираем внешние пробелы
    raw = raw.strip()
    
    # 2. Убираем кавычки
    if len(raw) >= 2 and ((raw.startswith('"') and raw.endswith('"')) or 
                          (raw.startswith("'") and raw.endswith("'"))):
        raw = raw[1:-1]
        # После удаления кавычек снова убираем пробелы
        raw = raw.strip()

    # 3. Булевы значения
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False

    # 4. Попытка превратить в число
    try:
        # Проверяем, что строка состоит только из цифр
        if raw.lstrip('-').isdigit():
            return int(raw)
    except ValueError:
        pass

    # 5. Возвращаем как строку
    return raw


def parse_insert(args):
    if len(args) < 5 or args[1].lower() != "into" or args[3].lower() != "values":
        raise ValueError("Неверный формат INSERT. Ожидалось: insert into <таблица> values (...)")

    table_name = args[2]
    values_part = " ".join(args[4:])

    match = re.search(r"\((.*)\)", values_part)
    if not match:
        raise ValueError("Не удалось найти значения в скобках. Ожидался формат: values (v1, v2, ...)")

    raw_values = match.group(1).strip()
    if not raw_values:
        raise ValueError("Пустые значения в скобках.")

    parsed_values = []
    for val in raw_values.split(","):
        val = val.strip()
        if not val:
            continue

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        else:
            if val.lstrip("-").isdigit():
                val = int(val)
            elif val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False

        parsed_values.append(val)

    if not parsed_values:
        raise ValueError("Не найдено ни одного значения.")

    return table_name, parsed_values

def _parse_condition(cond_str: str) -> dict[str, Any]:
    match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$', cond_str.strip())
    if not match:
        raise ValueError(f"Неверный формат условия: '{cond_str}'. Ожидалось col = value")
    col, raw_val = match.group(1), match.group(2).strip()
    val = _parse_value(raw_val)
    return {col: val}


def parse_select(args: list[str]) -> tuple[str, dict[str, Any] | None]:
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Неверный синтаксис SELECT. Формат: select from <таблица> [where col = value]")
    table_name = args[2]
    where_clause = None
    if len(args) >= 5 and args[3] == "where":
        where_clause = _parse_condition(args[4])
    return table_name, where_clause


def parse_update(args: list[str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
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


def parse_delete(args: list[str]) -> tuple[str, dict[str, Any]]:
    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        raise ValueError("Неверный синтаксис DELETE. Формат: delete from <таблица> where col = val")
    table_name = args[2]
    where_values = _parse_condition(args[4])
    return table_name, where_values