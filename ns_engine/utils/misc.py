from os import name as os_name
from os.path import abspath, dirname

def set_console_title(title):
    if os_name == "nt":
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW(title)
    else:
        from sys import stdout
        stdout.write(f"\x1b]2;{title}\x07")
        stdout.flush()

def convert_to_snake_case(input_string: str) -> str:
    result = ""
    for char in input_string:
        if char.isupper():
            result += "_" + char.lower()
        else:
            result += char

    if result.startswith("_"):
        result = result[1:]
    return result

def index_exists(list_or_tuple: list | tuple, index: int) -> bool:
    try:
        _ = list_or_tuple[index]
        return True
    except IndexError:
        return False
                    
def try_get(list_or_tuple: list | tuple, index: int, default = None):
    if index_exists(list_or_tuple, index):
        return list_or_tuple[index]
    return default

def try_set(list_or_tuple: list | tuple, index: int, value = None):
    if index_exists(list_or_tuple, index):
        list_or_tuple[index] = value
        return True
    return False

def try_del(list_or_tuple: list | tuple, index):
    if index_exists(list_or_tuple, index):
        del list_or_tuple[index]
        return True
    return False 

def remove_none_elements(list: list) -> list:
    return [item for item in list if item is not None]

def get_abs_path(path: str):
    return dirname(abspath(path))
