from os import name as os_name, getcwd as os_getcwd, chdir as os_chdir
from contextlib import contextmanager

def set_console_title(title):
    if os_name == "nt":
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW(title)

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

@contextmanager
def temp_cwd(temp_dir: str):
    original_dir = os_getcwd()
    try:
        os_chdir(temp_dir)
        yield
    finally:
        os_chdir(original_dir)