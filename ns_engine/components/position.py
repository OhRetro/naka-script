from dataclasses import dataclass
from typing import Self

@dataclass
class Position:
    index: int
    line: int
    column: int
    
    filename: str
    filedata: str
    
    def advance(self, current_char: str = None) -> Self:
        self.index += 1
        self.column += 1
        
        if current_char == "\n":
            self.line += 1
            self.column = 0
            
        return self
    
    def copy(self) -> Self:
        return Position(self.index, self.line, self.column, self.filename, self.filedata)
    
    def __int__(self) -> int:
        return self.index
    