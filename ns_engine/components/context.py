from dataclasses import dataclass, field
from typing import Self
from .position import Position

@dataclass(slots=True)
class Context:
    name: str
    parent: Self = field(default=None)
    parent_entry_pos: Position = field(default=None)
    