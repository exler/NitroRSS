from django.utils import timezone

from .engine import send_all
from .models import Message, MessageLog


def send_mail() -> None:
    send_all()


def retry_deferred() -> str:
    """
    Attempt to resend all deferred messages.
    """
    count = Message.objects.retry_deferred(new_priority=Message.DEFAULT_PRIORITY)
    return "%s message(s) retried" % count


def clean_old_logs() -> str:
    logs_deleted = MessageLog.objects.filter(date_published__lt=timezone.now() - timezone.timedelta(days=30)).delete()[
        0
    ]

    return f"Deleted {logs_deleted} old logs."
