from .utils import ensure_data_dir, load_metadata
from .parser import parse_insert, parse_select, parse_update, parse_delete, parse_create_table
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

            if command == "create_table":
                try:
                    table_name, schema = parse_create_table(args)
                    result = create_table(table_name, schema)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")

            elif command == "insert":
                try:
                    table_name, values_dict = parse_insert(args)
                    result = insert_row(table_name, values_dict)
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
                print("create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу")
                print("insert into <таблица> key1:value1 key2:value2 ... - вставить строку")
                print("select from <таблица> [where key:value] - выбрать строки")
                print("update <таблица> set key1:value1 ... where key:value - обновить строки")
                print("delete from <таблица> where key:value - удалить строки")
                print("list_tables - показать список таблиц")
                print("drop_table <имя> - удалить таблицу")
                print("help - справка")
                print("exit - выход")

            else:
                print("Неизвестная команда. Доступные: create_table, insert, select, update, delete, list_tables, drop_table, help, exit.")

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()