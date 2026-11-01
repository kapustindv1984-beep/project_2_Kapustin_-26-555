import json
from pathlib import Path
from prompt import string

DATA_FILE = Path("data.json")

def load_data() -> list:
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            print("Предупреждение: не удалось прочитать data.json, используется пустой список.")
    return []

def save_data(data: list) -> bool:
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Ошибка сохранения файла: {e}")
        return False

def show_menu() -> str:
    print("\n<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("<command> add - добавить запись")
    print("<command> list - показать все записи")
    print("<command> delete <номер> - удалить запись по номеру")
    return string("Введите команду: ")

def handle_command(cmd: str) -> bool:
    cmd = cmd.strip().lower()
    data = load_data()

    if cmd == "exit":
        print("До свидания!")
        return False

    elif cmd == "help":
        print("Доступные команды: exit, help, add, list, delete <номер>")
        return True

    elif cmd == "add":
        entry = string("Введите текст записи: ")
        if entry:
            data.append(entry)
            if save_data(data):
                print("Запись добавлена.")
            else:
                print("Не удалось сохранить запись.")
        else:
            print("Пустая запись не добавлена.")
        return True

    elif cmd == "list":
        if not data:
            print("Записей пока нет.")
        else:
            for i, entry in enumerate(data, start=1):
                print(f"{i}. {entry}")
        return True

    elif cmd.startswith("delete "):
        arg = cmd[len("delete "):].strip()
        if arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(data):
                removed = data.pop(idx)
                if save_data(data):
                    print(f"Запись удалена: {removed}")
                else:
                    print("Не удалось сохранить изменения после удаления.")
                    # возвращаем обратно, если сохранение не удалось
                    data.insert(idx, removed)
            else:
                print("Нет записи с таким номером.")
        else:
            print("Используйте: delete <номер>, например: delete 1")
        return True

    else:
        print(f"Неизвестная команда: {cmd}")
        return True

def main():
    print("DB project is running!")
    while True:
        command = show_menu()
        if not handle_command(command):
            break

if __name__ == "__main__":
    main()