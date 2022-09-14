import os.path
from typing import Any
from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.forms import BoundField
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString

from nitrorss.utils.url import get_full_url

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


@register.filter("baseurl")
@stringfilter
def base_url(value: str) -> str:
    return urlparse(value).netloc


@register.simple_tag
def static_base_url(path: str) -> str:
    return get_full_url(os.path.join(settings.STATIC_URL, path))
