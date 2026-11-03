import shutil
import sys
from pathlib import Path

import pytest

# --- НАСТРОЙКА ПУТЕЙ ---
test_dir = Path(__file__).resolve().parent
project_root = test_dir.parent  # H2

src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# --- ИМПОРТЫ МОДУЛЕЙ (только после добавления пути) ---
from primitive_db import core
from primitive_db.constants import DATA_DIR
from primitive_db.core import (
    create_table,
    delete_rows,
    drop_table,
    insert_row,
    select_rows,
    update_rows,
)


@pytest.fixture(autouse=True)
def _clean_db():
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    core._select_cache = core.create_cacher()
    yield
    shutil.rmtree(DATA_DIR, ignore_errors=True)


def test_create_table_and_validation():
    result = create_table("users", {"name": "str", "age": "int", "active": "bool"})
    assert "успешно создана" in result.lower()

    with pytest.raises(TypeError, match="не поддерживается"):
        create_table("bad_type", {"val": "unknown_type"})

    with pytest.raises(ValueError, match="уже существует"):
        create_table("users", {"name": "str"})


def test_insert_row_and_id_auto_increment():
    create_table("users", {"name": "str", "age": "int"})

    res1 = insert_row("users", ["Alice", 25])
    assert "Новый ID: 1" in res1

    res2 = insert_row("users", ["Bob", 30])
    assert "Новый ID: 2" in res2

    with pytest.raises(ValueError, match="ожидается"):
        insert_row("users", ["Charlie"])

    with pytest.raises(ValueError, match="тип значения"):
        insert_row("users", ["David", "thirty"])


def test_select_with_filtering():
    create_table("users", {"name": "str", "age": "int"})
    insert_row("users", ["Alice", 25])
    insert_row("users", ["bob", 30])
    insert_row("users", ["Лёша", 22])

    all_rows = select_rows("users")
    assert len(all_rows) == 3

    alice_rows = select_rows("users", {"name": "alice"})
    assert len(alice_rows) == 1
    assert alice_rows[0][1] == "Alice"

    bob_rows = select_rows("users", {"name": "BOB"})
    assert len(bob_rows) == 1
    assert bob_rows[0][1] == "bob"


def test_update_and_delete():
    create_table("users", {"name": "str", "age": "int"})
    insert_row("users", ["Alice", 25])
    insert_row("users", ["Bob", 30])

    upd_res = update_rows("users", {"age": 26}, {"name": "alice"})
    assert "Обновлено записей: 1" in upd_res

    updated_row = select_rows("users", {"name": "alice"})
    assert updated_row[0][2] == 26

    del_res = delete_rows("users", {"name": "bob"})
    assert "Удалено записей: 1" in del_res

    remaining = select_rows("users")
    assert len(remaining) == 1


def test_drop_table_with_confirmation(monkeypatch):
    create_table("users", {"name": "str"})
    insert_row("users", ["Alice"])

    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert len(select_rows("users")) == 1

    create_table("users2", {"name": "str"})
    insert_row("users2", ["Bob"])

    monkeypatch.setattr("builtins.input", lambda _: "y")
    res_drop = drop_table("users2")
    assert "удалена" in res_drop.lower()

    with pytest.raises(KeyError, match="не найдена"):
        select_rows("users2")


def test_error_handling():
    data_path = Path(DATA_DIR)
    shutil.rmtree(data_path, ignore_errors=True)

    with pytest.raises((ValueError, KeyError, IOError)):
        select_rows("nonexistent")


def test_select_caching():
    create_table("users", {"name": "str", "age": "int"})
    insert_row("users", ["Alice", 25])

    rows1 = select_rows("users", {"age": 25})
    assert len(rows1) == 1

    rows2 = select_rows("users", {"age": 25})
    assert rows2 == rows1

    insert_row("users", ["Bob", 26])
    rows3 = select_rows("users", {"age": 25})
    assert rows3 == rows1
