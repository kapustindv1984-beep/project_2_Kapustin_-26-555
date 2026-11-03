from primitive_db.parser import _parse_value

tests = [
    '"Alice"',
    '" Alice "',
    '25',
    '"25"',
    'true',
]

for t in tests:
    print(f"Вход: {t!r:12} → Выход: {_parse_value(t)!r}")