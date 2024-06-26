from os import name as os_name, getcwd as os_getcwd, chdir as os_chdir
from os.path import abspath as osp_abspath, isfile as osp_isfile
from contextlib import contextmanager
from re import compile as re_compile

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
    
def clean_filetextdata(text: str) -> str:
    new_text_in_lines = []
    
    for text_line in text.split("\n"):
        text_line = text_line.strip()
        # if not text_line: continue
        new_text_in_lines.append(text_line)

    return "\n".join(new_text_in_lines)
    
def get_filedata(filename: str) -> str:
    file_abspath = osp_abspath(filename)
    
    #! It's not in a try-except block by design
    if not osp_isfile(file_abspath):
        raise FileNotFoundError(f"The provided path is not a file: '{file_abspath}'")
        
    with open(file_abspath, "r", encoding="utf-8") as f:
        return clean_filetextdata(f.read())

def look_like_path(string: str) -> bool:
    path_pattern = re_compile(
        r"^(\/|\\|[a-zA-Z]:\\|\.\/|\.\.\/|[^\/\\]+\/|[^\/\\]+\\)"
    )
    
    return path_pattern.match(string)
