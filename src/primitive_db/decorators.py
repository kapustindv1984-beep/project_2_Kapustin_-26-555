import time
from functools import wraps


def handle_db_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def confirm_action(action_name: str):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if response != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result

    return wrapper


def create_cacher():

    cache = {}

    def cache_result(key, value_func, *args, **kwargs):
        if key in cache:
            return cache[key]
        result = value_func(*args, **kwargs)
        cache[key] = result
        return result

    return cache_result
