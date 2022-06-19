from typing import Any


class HideColonFormMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["label_suffix"] = ""
        super().__init__(*args, **kwargs)
