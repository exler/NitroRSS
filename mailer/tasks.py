from celery import shared_task

from .engine import send_all
from .models import Message


@shared_task
def send_mail() -> None:
    send_all()


@shared_task
def retry_deferred() -> str:
    """
    Attempt to resend all deferred messages.
    """
    count = Message.objects.retry_deferred()
    return "%s message(s) retried" % count
