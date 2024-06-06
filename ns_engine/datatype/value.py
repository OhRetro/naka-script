from dataclasses import dataclass
from typing import Any

@dataclass(order=True)
class Value:
    value: Any

    def set_context(self, context = None):
        self.context = context
        return self

    