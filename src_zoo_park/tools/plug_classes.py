from typing import Any


class UnityPlug:
    name = ""
    format_name = ""

    def __getattr__(self, item: str) -> Any:
        return None
