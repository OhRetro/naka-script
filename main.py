from typing import Optional
from sys import argv as sys_argv
from os.path import abspath as osp_abspath, isfile as osp_isfile
from ns_engine import __version__ as ns_version, wrapper as ns_wrapper

def argument(shortflag: str, flag: str) -> bool:
    return (shortflag in sys_argv and shortflag != None) or (flag in sys_argv and flag != None)

def get_filedata(filename: str) -> Optional[str]:
    file_abspath = osp_abspath(filename)
    try:
        if not osp_isfile(file_abspath):
            raise FileNotFoundError()
            
        with open(file_abspath, "r", encoding="utf-8") as f:
            return f.read()
        
    except FileNotFoundError:
        print(f"File not found: '{file_abspath}'")
        return None
    
def shell():
    print(f"Welcome to NakaScript v{ns_version} Shell")
    while True:
        try:
            command_text = input(">>> ")
            if not command_text.strip(): continue
            result, error = ns_wrapper.interpret("<shell>", command_text)
            
            if error: print(error.as_string())
            elif result:
                to_print = repr(result if len(result.value) > 1 else result.value[0])
                print(to_print)
            
        except KeyboardInterrupt:
            break

def run(filename: str):
    source_code = get_filedata(filename)    
    if source_code is None or not source_code.strip(): return

    try:
        _, error = ns_wrapper.interpret(filename, source_code)
        if error: print(error.as_string())
        
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    args_len = len(sys_argv) - 1
    is_first_arg_scriptfile = False
    
    if args_len >= 1:
        first_arg = sys_argv[1]
        is_first_arg_scriptfile = first_arg
    
    if is_first_arg_scriptfile:
        run(first_arg)
    else:
        if not args_len:
            shell()
                
        elif argument("-v", "--version"):
            print(f"v{ns_version}")
        