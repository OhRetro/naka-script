from logging import basicConfig as logg_basicConfig, log as logg_log, DEBUG as logg_DEBUG
from inspect import currentframe as i_currentframe, getouterframes as i_getouterframes

logg_basicConfig(format = "[%(levelname)s]: %(message)s", level = logg_DEBUG, encoding = "utf-8")

DEFAULT_ENABLED = 1
ALL_USES_DEFAULT = 0

COMPONENTS_ENABLED = {
    "lexer.py": 0,
    "parser.py": 0,
    "interpreter.py": 0,
    
    "run.py": 0,
    
    "context.py": 0,
    "node.py": 0,
    "token.py": 0
}

DEFAULT_LOG_MESSAGE = "[MESSAGE NOT SET]"

class DebugMessage:
    def __init__(self):
        curframe = i_currentframe()
        calframe = i_getouterframes(curframe, 2)
        self.caller = calframe[1][1].replace("\\", "/").split("/")[-1].lower()
        
        self.set_enabled(COMPONENTS_ENABLED.get(self.caller, DEFAULT_ENABLED) if not ALL_USES_DEFAULT else DEFAULT_ENABLED)
        
    def log(self, message: str = DEFAULT_LOG_MESSAGE):
        if not self.enabled: return
        curframe = i_currentframe()
        calframe = i_getouterframes(curframe, 2)
 
        logg_log(logg_DEBUG, f"[{self.caller}]: [{calframe[2][3]}]: {message}")
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        return self
    