import re

def _parse_value(val_str: str):
    val_str = val_str.strip()
    if val_str.lower() == "true":
        return True
    elif val_str.lower() == "false":
        return False
    elif re.match(r'^-?\d+$', val_str):
        return int(val_str)
    # Если строка в кавычках — убираем кавычки
    elif (val_str.startswith('"') and val_str.endswith('"')) or \
         (val_str.startswith("'") and val_str.endswith("'")):
        return val_str[1:-1]
    return val_str


def parse_insert(args: list) -> tuple:
    # Ожидаем: insert into <table> values (<v1>, <v2>, ...)
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        raise ValueError("Некорректный синтаксис INSERT. Используйте: insert into table values (v1, v2, ...)")

    table_name = args[2]
    values_str = " ".join(args[4:])

    if not (values_str.startswith("(") and values_str.endswith(")")):
        raise ValueError("Значения должны быть в скобках: (v1, v2, ...)")
    values_str = values_str[1:-1].strip()

    tokens = []
    current = ""
    in_quotes = False
    quote_char = None

    for ch in values_str:
        if ch in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = ch
            continue
        elif ch == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            tokens.append(current)
            current = ""
            continue

        if in_quotes:
            current += ch
        else:
            if ch == ",":
                if current.strip():
                    tokens.append(current.strip())
                current = ""
            else:
                current += ch

    if current.strip():
        tokens.append(current.strip())

    values = [_parse_value(t) for t in tokens]
    return table_name, values


def parse_select(args: list) -> tuple:
    # Ожидаем: select from <table> [where <col> = <val>]
    if len(args) < 3 or args[1] != "from":
        raise ValueError("Некорректный синтаксис SELECT. Используйте: select from table [where col = val]")

    table_name = args[2]
    where_clause = None

    where_index = None
    for i, w in enumerate(args):
        if w == "where":
            where_index = i
            break

    if where_index is not None:
        # where <col> = <val>
        if where_index + 2 >= len(args) or args[where_index + 1] != "=":
            raise ValueError("Некорректное условие WHERE. Используйте: where col = val")
        col = args[where_index - 1]  # это колонка
        val = args[where_index + 2]  # это значение
        where_clause = {col: _parse_value(val)}

    return table_name, where_clause


def parse_update(args: list) -> tuple:
    # update <table> set <col> = <val> where <col2> = <val2>
    # Пример: update users set age = 26 where name = Alice
    if len(args) < 8 or args[2] != "set" or args[4] != "=" or args[6] != "where" or args[8] != "=":
        raise ValueError("Некорректный синтаксис UPDATE. Используйте: update table set col = val where col = val")

    table_name = args[1]
    set_col = args[3]
    set_val = _parse_value(args[5])
    where_col = args[7]
    where_val = _parse_value(args[9])

    return table_name, {set_col: set_val}, {where_col: where_val}


def parse_delete(args: list) -> tuple:
    # delete from <table> where <col> = <val>
    if len(args) < 6 or args[1] != "from" or args[3] != "where" or args[5] != "=":
        raise ValueError("Некорректный синтаксис DELETE. Используйте: delete from table where col = val")

    table_name = args[2]
    col = args[4]
    val = _parse_value(args[6])

    return table_name, {col: val}