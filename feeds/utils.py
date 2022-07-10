from datetime import datetime
from time import mktime
from typing import Optional

from django.utils.timezone import make_aware


def struct_time_to_datetime(struct_time: Optional[tuple]) -> datetime:
    """
    Function that converts a struct_time tuple to a datetime object.
    Additionally, makes the datetime object timezone-aware.

    If struct_time is `None`, then return `None`.

    Args:
        struct_time (tuple | None): Struct time tuple to convert.

    Returns:
        datetime: Datetime object.
    """
    return make_aware(datetime.fromtimestamp(mktime(struct_time))) if struct_time else None
