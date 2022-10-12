import contextlib
import logging
import smtplib
from enum import Enum
from typing import ContextManager, Iterable, Optional, Type

from django.conf import global_settings
from django.core.mail import get_connection
from django.db import OperationalError, transaction

from .models import Message, MessageLog

logger = logging.getLogger(__name__)


class SendAction(str, Enum):
    SENT = "sent"
    DEFERRED = "deferred"


@contextlib.contextmanager
def sender_context(message: Message) -> None:
    """
    Makes a context manager appropriate for sending a message.
    Entering the context using `with` may return a `None` object if the message
    has been sent/deleted already.
    """
    with transaction.atomic():
        try:
            yield Message.objects.filter(pk=message.pk).select_for_update(nowait=True).get()
        except Message.DoesNotExist:
            # Already deleted
            yield None
        except OperationalError:
            # Already locked
            yield None


def get_messages_for_sending(messages: Optional[Iterable[Message]] = None) -> Iterable[ContextManager]:
    """
    Returns a series of context managers that are used for sending mails in the queue.
    Entering the context manager returns the actual message.
    """
    if messages is None:
        messages = Message.objects.prioritize()

    for message in messages:
        yield sender_context(message)


def send_messages(messages: Optional[Iterable[Message]] = None) -> None:
    """
    Send eligible messages in the queue.

    If messages is None, all eligible messages will be sent.
    """
    email_backend = global_settings.EMAIL_BACKEND

    counts = {e.value: 0 for e in SendAction}

    connection = None
    for message_context in get_messages_for_sending(messages):
        with message_context as message:
            if message is None:
                # Lock not acquired
                continue

            try:
                if connection is None:
                    connection = get_connection(backend=email_backend)

                email = message.email
                if email is not None:
                    email.connection = connection
                    email.send()

                    # Connection can't be stored in the MessageLog
                    email.connection = None
                    message.email = email  # For the sake of MessageLog
                    MessageLog.log(message, MessageLog.Results.SUCCESS)
                    counts[SendAction.SENT] += 1
                else:
                    logger.warning("Message discarded due to failure in conversion from DB")

                message.delete()

            except Exception as exc:
                handle_delivery_exception(message, exc)
                counts[SendAction.DEFERRED] += 1

                connection = None

    logger.info("Sent messages", extra=counts)


def handle_delivery_exception(message: Message, exc: Type[BaseException]) -> None:
    if isinstance(
        exc,
        (
            smtplib.SMTPAuthenticationError,
            smtplib.SMTPDataError,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPSenderRefused,
            IOError,
        ),
    ):
        message.defer()
        logging.info("Message deferred due to failure: %s", exc)
        MessageLog.log(message, MessageLog.Results.FAILURE, log_message=str(exc))

    raise exc
