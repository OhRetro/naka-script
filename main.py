from sys import argv as sys_argv
from ns_engine import __version__ as ns_version, wrapper as ns_wrapper
from ns_engine.utils.misc import get_filedata, look_like_path

def argument(shortflag: str, flag: str) -> bool:
    return (shortflag in sys_argv and shortflag != None) or (flag in sys_argv and flag != None)

def shell():
    print(f"Welcome to NakaScript v{ns_version} Shell")
    while True:
        try:
            command_text = input(">>> ")
            if not command_text.strip(): continue
            result, error, _ = ns_wrapper.interpret("<shell>", command_text)
            
            if error: print(error.as_string())
            elif result:
                to_print = repr(result if len(result.value) > 1 else result.value[0])
                print(to_print)
            
        except KeyboardInterrupt:
            break

def run(filename: str):
    try:
        source_code = get_filedata(filename)
            
    except FileNotFoundError as e:
        print(f"Failed to load script \"{filename}\": {e}")
        source_code = None
         
    if source_code is None or not source_code.strip(): return

    try:
        _, error, _ = ns_wrapper.interpret(filename, source_code)
        if error: print(error.as_string())
        
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    args_len = len(sys_argv) - 1
    is_first_arg_scriptfile = False
    
    if args_len >= 1:
        first_arg = sys_argv[1]
        is_first_arg_scriptfile = look_like_path(first_arg)
    
    if is_first_arg_scriptfile:
        run(first_arg)
    else:
        if not args_len:
            shell() 
        elif argument("-v", "--version"):
            print(f"v{ns_version}")
        