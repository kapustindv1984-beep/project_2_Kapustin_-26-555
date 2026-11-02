from .utils import ensure_data_dir, load_metadata
from .parser import parse_insert, parse_select, parse_update, parse_delete
from .core import create_table, insert_row, select_rows, update_rows, delete_rows, drop_table
from prettytable import PrettyTable


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

            # ВАЖНО: здесь начинается главный if, без него elif не работает!
            if command == "create_table":
                if len(args) < 3:
                    print("Ошибка: недостаточно аргументов. Формат: create_table <имя> <col:type> ...")
                    continue

                table_name = args[1]
                schema_str = " ".join(args[2:])
                schema = {}
                
                for part in schema_str.split():
                    if ":" in part:
                        col, dtype = part.split(":", 1)
                        schema[col] = dtype
                    else:
                        print(f"Ошибка: неверный формат колонки '{part}'. Ожидалось col:type")
                        continue

                if not schema:
                    print("Ошибка: не удалось распознать ни одной колонки в формате col:type")
                    continue

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
                        continue

                    if len(rows) == 0:
                        print("Пусто.")
                        continue

                    metadata = load_metadata()
                    # Защита на случай, если метаданные пусты
                    if not metadata or table_name not in metadata:
                        print("Метаданные таблицы недоступны.")
                        continue
                        
                    schema = metadata[table_name]["schema"]
                    headers = list(schema.keys())

                    t = PrettyTable()
                    t.align = "l"
                    t.field_names = headers
                    for row in rows:
                        t.add_row(row)

                    print(t)
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
            
            elif command == "list_tables":
                metadata = load_metadata()
                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    t = PrettyTable()
                    t.align = "l"
                    t.field_names = ["Имя таблицы", "Колонки"]
                    for table_name, info in metadata.items():
                        cols = ", ".join(f"{col}:{dtype}" for col, dtype in info["schema"].items())
                        t.add_row([table_name, cols])
                    print(t)

            elif command == "drop_table":
                if len(args) < 2:
                    print("Ошибка: укажите имя таблицы. Формат: drop_table <имя>")
                    continue
                
                table_name = args[1]
                result = drop_table(table_name)
                print(result)

            elif command == "help":
                print("***Процесс работы с таблицей***")
                print("Функции:")
                print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
                print("<command> list_tables - показать список всех таблиц")
                print("<command> drop_table <имя_таблицы> - удалить таблицу")
                print("<command> exit - выход из программы")
                print("<command> help - справочная информация")

            else:
                print("Неизвестная команда. Доступные: create_table, insert, select, update, delete, list_tables, drop_table, help, exit.")

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()