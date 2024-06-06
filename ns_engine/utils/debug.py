from logging import basicConfig, log, DEBUG
from inspect import currentframe as i_currentframe, getouterframes as i_getouterframes

basicConfig(format = "[%(levelname)s]: %(message)s", level = DEBUG, encoding = "utf-8")

DEFAULT_ENABLED = 1
ALL_USES_DEFAULT = 0

COMPONENTS_ENABLED = {
    "context.py": 0,
    "interpreter.py": 0,
    "node.py": 0,
    "parser.py": 0,
    "symbol_table.py": 0,
    "token.py": 0,
    "run.py": 0
}

class DebugMessage:
    def __init__(self):
        curframe = i_currentframe()
        calframe = i_getouterframes(curframe, 2)
        self.caller = calframe[1][1].replace("\\", "/").split("/")[-1].lower()
        
        self.set_enabled(COMPONENTS_ENABLED.get(self.caller, DEFAULT_ENABLED) if not ALL_USES_DEFAULT else DEFAULT_ENABLED)
        
    def display(self, message: str):
        if not self.enabled: return
        curframe = i_currentframe()
        calframe = i_getouterframes(curframe, 2)
 
        log(DEBUG, f"[{self.caller}]: [{calframe[2][3]}]: {message}")
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        return self
    