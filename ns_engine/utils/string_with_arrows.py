from ..components.position import Position

def string_with_arrows(text: str, pos_start: Position, pos_end: Position):
    result = ""

    # Calculate indices
    index_start = max(text.rfind("\n", 0, pos_start.index), 0)
    index_end = text.find("\n", index_start + 1)
    if index_end < 0: index_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[index_start:index_end]
        column_start = pos_start.column if i == 0 else 0
        column_end = pos_end.column if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * column_start + "^" * (column_end - column_start)

        # Re-calculate indices
        index_start = index_end
        index_end = text.find("\n", index_start + 1)
        if index_end < 0: index_end = len(text)

    return result.replace("\t", "")

def n_string_with_arrows(text: str, pos_start: Position, pos_end: Position):
    result = ""
    
    text = text.split("\n")[pos_start.line]
    pos_end = pos_start
    
    # Calculate indices
    index_start = max(text.rfind("\n", 0, pos_start.index), 0)
    index_end = text.find("\n", index_start + 1)
    if index_end < 0: index_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 2
    for i in range(line_count):
        # Calculate line columns
        line = text[index_start:index_end]
        column_start = pos_start.column if i == 0 else 0
        column_end = pos_end.column if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * column_start + "^" * (column_end - column_start)

        # Re-calculate indices
        index_start = index_end
        index_end = text.find("\n", index_start + 1)
        if index_end < 0: index_end = len(text)

    return result.replace("\t", "")