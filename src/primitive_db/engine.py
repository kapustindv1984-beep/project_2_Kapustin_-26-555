import sys
from .utils import ensure_data_dir
from .parser import parse_insert, parse_select, parse_update, parse_delete
from .core import create_table, insert_row, select_rows, update_rows, delete_rows

def main():
    ensure_data_dir()
    print("Primitive DB ready. Type 'exit' to quit.")
    
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
            if cmd.lower() == "exit":
                print("Bye!")
                break

            args = cmd.split()
            command = args[0].lower()

            if command == "create" and len(args) >= 4 and args[1] == "table":
                # create table users name:str age:int
                table_name = args[2]
                schema_str = " ".join(args[3:])
                schema = {}
                for part in schema_str.split():
                    if ":" in part:
                        col, dtype = part.split(":", 1)
                        schema[col] = dtype
                result = create_table(table_name, schema)
                print(result)

            elif command == "insert":
                try:
                    table_name, values = parse_insert(args)
                    result = insert_row(table_name, values)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")

            elif command == "select":
                try:
                    table_name, where_clause = parse_select(args)
                    rows = select_rows(table_name, where_clause)
                    if rows is None:
                        print("Таблица не найдена.")
                    elif len(rows) == 0:
                        print("Пусто.")
                    else:
                        print(f"Всего строк: {len(rows)}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif command == "update":
                try:
                    table_name, set_data, where_data = parse_update(args)
                    result = update_rows(table_name, set_data, where_data)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")

            elif command == "delete":
                try:
                    table_name, where_data = parse_delete(args)
                    result = delete_rows(table_name, where_data)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")
            
            else:
                print("Неизвестная команда. Доступные: create, insert, select, update, delete.")

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()