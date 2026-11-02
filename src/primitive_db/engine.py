from typing import List
from .parser import parse_insert, parse_select, parse_update, parse_delete
from .core import create_table, insert_row, select_rows, update_rows, delete_rows, load_metadata
from .constants import META_FILE, DATA_DIR
from .utils import ensure_data_dir

def init_db():
    ensure_data_dir()
    # Метафайл создастся автоматически при первом create_table

def execute_command(args: List[str]) -> str:
    if not args:
        return "Пустая команда."
    
    cmd = args.lower()
    
    if cmd == "create":
        # Формат: create table users name:str age:int
        if len(args) < 4 or args != "table":
            return "Некорректный синтаксис CREATE. Используйте: create table <name> <col1:type> <col2:type>..."
        
        table_name = args
        schema = {}
        for col_def in args[3:]:
            if ":" not in col_def:
                return f"Неверный формат колонки: {col_def}. Используйте name:type"
            col_name, col_type = col_def.split(":", 1)
            schema[col_name] = col_type
        
        if create_table(table_name, schema):
            return f"Таблица '{table_name}' создана."
        else:
            return f"Не удалось создать таблицу '{table_name}' (возможно, уже существует или неверный тип)."
    
    elif cmd == "insert":
        try:
            table_name, values = parse_insert(args)
            meta = load_metadata()
            
            if table_name not in meta:
                return f"Таблица '{table_name}' не найдена. Создайте её через create table."
            
            schema_cols = list(meta[table_name]["schema"].keys())
            if len(values) != len(schema_cols):
                return f"Ошибка: ожидается {len(schema_cols)} значений, передано {len(values)}."
            
            row = dict(zip(schema_cols, values))
            if insert_row(table_name, row):
                return "Запись добавлена."
            else:
                return "Ошибка валидации типов при вставке."
        except ValueError as e:
            return str(e)
    
    elif cmd == "select":
        try:
            table_name, where = parse_select(args)
            rows = select_rows(table_name, where)
            
            if not rows:
                return "Нет данных."
            
            if where:
                col, val = next(iter(where.items()))
                return f"Найдено строк по условию {col}={val}: {len(rows)}"
            return f"Всего строк: {len(rows)}"
        except ValueError as e:
            return str(e)
    
    elif cmd == "update":
        try:
            table_name, set_vals, where = parse_update(args)
            count = update_rows(table_name, set_vals, where)
            return f"Обновлено строк: {count}"
        except ValueError as e:
            return str(e)
    
    elif cmd == "delete":
        try:
            table_name, where = parse_delete(args)
            count = delete_rows(table_name, where)
            return f"Удалено строк: {count}"
        except ValueError as e:
            return str(e)
    
    elif cmd == "exit":
        return "EXIT"
    
    else:
        return f"Неизвестная команда: {cmd}. Доступные: create, insert, select, update, delete, exit."

def run_cli():
    init_db()
    print("Primitive DB ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            args = user_input.split()
            result = execute_command(args)
            if result == "EXIT":
                break
            print(result)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Критическая ошибка: {e}")