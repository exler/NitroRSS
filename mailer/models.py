from typing import Optional

from django.core.mail import EmailMessage
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from mailer.utils import EmailDatabaseSerializer
from nitrorss.common.models import TimestampedModel


class Message(TimestampedModel):
    """
    Email stored for later sending.
    """

    class Priorities(models.IntegerChoices):
        DEFERRED = 0, _("Deferred")
        LOW = 10, _("Low")
        MEDIUM = 20, _("Medium")
        HIGH = 30, _("High")

    DEFAULT_PRIORITY = Priorities.MEDIUM

    # Message data is a pickled EmailMessage - interact using the `email` property
    _message_data = models.TextField()

    priority = models.PositiveSmallIntegerField(choices=Priorities.choices, default=DEFAULT_PRIORITY)

    @property
    def email(self) -> EmailMessage:
        return EmailDatabaseSerializer.db_to_email(self._message_data)

    @email.setter
    def email(self, value: EmailMessage) -> None:
        self._message_data = EmailDatabaseSerializer.email_to_db(value)

    @cached_property
    def recipients(self) -> list[str]:
        email = self.email
        if email is not None:
            return email.to
        else:
            return []

    @cached_property
    def subject(self) -> str:
        email = self.email
        if email is not None:
            return email.subject
        else:
            return ""

    @classmethod
    def make(
        cls,
        subject: str,
        body: str,
        recipients: list[str],
        from_email: Optional[str] = None,
        attachments: list[str] = [],
        priority: Optional[int] = None,
    ) -> "Message":
        priority = priority if priority else cls.DEFAULT_PRIORITY
        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=recipients, attachments=attachments)
        db_msg = Message(email=email, priority=priority)
        return db_msg


class MessageLog(models.Model):
    """
    A log entry which stores the result and optionally a log message for
    an attempt to send a Message.
    """

    class Results(models.IntegerChoices):
        SUCCESS = 0, _("Success")
        FAILURE = 1, _("Failure")

    result = models.PositiveSmallIntegerField(choices=Results.choices)
    log_message = models.TextField()
