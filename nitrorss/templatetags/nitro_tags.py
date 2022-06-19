from typing import Any

from django import template
from django.forms import BoundField
from django.utils.safestring import SafeString

register = template.Library()


class MissingTemplateWidget(Exception):
    def __init__(
        self,
        msg: str = "Cannot add class name to a non-widget object",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(msg, *args, **kwargs)


@register.filter("addclass")
def add_class(value: BoundField, arg: str) -> SafeString:
    try:
        return value.as_widget(attrs={"class": arg})
    except AttributeError:
        raise MissingTemplateWidget
