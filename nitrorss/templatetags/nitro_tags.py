from django import template
from django.forms import BoundField
from django.utils.safestring import SafeString

register = template.Library()


@register.filter("addclass")
def add_class(value: BoundField, arg: str) -> SafeString:
    return value.as_widget(attrs={"class": arg})
