from ns_engine import __version__ as ns_version
from ns_engine.tools.make_executable import make_executable
from sys import argv as sys_args

if __name__ == "__main__":
    if "mkexe" in sys_args:
        make_executable(ns_version.split("."))
