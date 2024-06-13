from ns_engine import __version__ as ns_version, wrapper as ns_wrapper
from sys import argv as sys_argv

def shell():
    print(f"Welcome to NakaScript v{ns_version} Shell")
    while True:
        try:
            command_text = input(">>> ")
            result, error = ns_wrapper.execute("<shell>", command_text)
            
            if error: print(error.as_string())
            elif result: print(repr(result))
            
        except KeyboardInterrupt:
            break
            
if __name__ == "__main__":
    if "exec" in sys_argv:
        ns_wrapper.make_executable()
    else:
        shell()
        