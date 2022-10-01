from .engine import send_all
from .models import Message


def send_mail() -> None:
    send_all()


def retry_deferred() -> str:
    """
    Attempt to resend all deferred messages.
    """
    count = Message.objects.retry_deferred(new_priority=Message.DEFAULT_PRIORITY)
    return "%s message(s) retried" % count
