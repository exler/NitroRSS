import json
from typing import Any


class ObjectEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "to_json"):
            return o.to_json()
        elif hasattr(o, "__dict__"):
            return o.__dict__

        return o
