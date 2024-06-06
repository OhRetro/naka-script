from dataclasses import dataclass

@dataclass(frozen=True)
class NSError:
    name: str
    details: str
    
    filename: str
    line: int

    def __str__(self) -> str:
        result = f"{self.name}: {self.details}\n"
        result += f"\tFile {self.filename}, line {self.line + 1}"
        return result


# Happens at Lexer Process
class NSIllegalCharacterError(NSError):
    def __init__(self, details: str, filename: str, line: int):
        super().__init__("Illegal Character Error", details, filename, line)

class NSExpectedCharacterError(NSError):
    def __init__(self, details: str, filename: str, line: int):
        super().__init__("Expected Character Error", details, filename, line)
        
class NSLoadingError(NSError):
    def __init__(self, details: str, filename: str, line: int):
        super().__init__("Loading Error", details, filename, line)

# Happens at AST Process
class NSInvalidSyntaxError(NSError):
    def __init__(self, details: str, filename: str, line: int):
        super().__init__("Invalid Syntax Error", details, filename, line)
