from os import system
from datetime import date

def make_executable(version: list[int]):
    today = date.today()
    day_month = today.strftime("%d%m%y")
    
    version.append(day_month)
    
    version_string = ".".join([str(x) for x in version])
    
    options = [
        "--standalone",
        "--onefile",
        #"--quiet",
        "--assume-yes-for-downloads",
        "--output-dir=build/",
        f"--output-filename=nakascript_runtime_v{version_string}"
        # #"--windows-icon-from-ico=logo.ico",
    ]

    _options = " ".join(options)
    system(f"nuitka {_options} main.py")
    