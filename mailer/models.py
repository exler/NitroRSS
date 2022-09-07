from typing import Optional

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from mailer.utils import EmailDatabaseSerializer
from nitrorss.common.models import TimestampedModel


class MessageDataPropertiesMixin:
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

    @cached_property
    def message_id(self) -> int | None:
        """
        From django.core.mail.message:

        Email header names are case-insensitive (RFC 2045),
        so we have to accommodate that when doing comparisons.
        """
        email = self.email
        if email is not None:
            for key, value in email.extra_headers.items():
                if key.lower() == "message-id":
                    return value
        else:
            return None


class MessageManager(models.Manager):
    def low_priority(self) -> models.QuerySet:
        return self.filter(priority=Message.Priorities.LOW)

    def medium_priority(self) -> models.QuerySet:
        return self.filter(priority=Message.Priorities.MEDIUM)

    def high_priority(self) -> models.QuerySet:
        return self.filter(priority=Message.Priorities.HIGH)

    def non_deferred(self) -> models.QuerySet:
        return self.exclude(priority=Message.Priorities.DEFERRED)

    def deferred(self) -> models.QuerySet:
        return self.filter(priority=Message.Priorities.DEFERRED)

    def retry_deferred(self, new_priority: int) -> int:
        return self.deferred().update(priority=new_priority)

    def prioritize(self) -> models.QuerySet:
        return self.non_deferred().order_by("priority", "created_at")


class Message(MessageDataPropertiesMixin, TimestampedModel):
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
    message_data = models.TextField()

    priority = models.PositiveSmallIntegerField(choices=Priorities.choices, default=DEFAULT_PRIORITY)

    objects = MessageManager()

    @property
    def email(self) -> EmailMessage:
        return EmailDatabaseSerializer.db_to_email(self.message_data)

    @email.setter
    def email(self, value: EmailMessage) -> None:
        self.message_data = EmailDatabaseSerializer.email_to_db(value)

    @classmethod
    def make(
        cls,
        subject: str,
        recipients: list[str],
        text_content: str,
        html_content: Optional[str] = None,
        from_email: Optional[str] = None,
        attachments: list[str] = [],
        priority: Optional[int] = None,
    ) -> "Message":
        priority = priority if priority else cls.DEFAULT_PRIORITY
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=recipients, attachments=attachments
        )
        if html_content:
            email.attach_alternative(html_content, "text/html")
        db_msg = Message(email=email, priority=priority)
        return db_msg


class MessageLog(MessageDataPropertiesMixin, models.Model):
    """
    A log entry which stores the result and optionally a log message for
    an attempt to send a Message.
    """

    class Results(models.IntegerChoices):
        SUCCESS = 0, _("Success")
        FAILURE = 1, _("Failure")

    message_data = models.TextField()
    priority = models.PositiveSmallIntegerField(choices=Message.Priorities.choices)

    when_added = models.DateTimeField(db_index=True)
    when_attempted = models.DateTimeField(auto_now_add=True)

    result = models.PositiveSmallIntegerField(choices=Results.choices)
    log_message = models.TextField()

    @property
    def email(self) -> EmailMessage:
        return EmailDatabaseSerializer.db_to_email(self.message_data)

    @classmethod
    def log(cls, message: Message, result: int, log_message: str = "") -> "MessageLog":
        return cls.objects.create(
            message_data=message.message_data,
            when_added=message.created_at,
            priority=message.priority,
            result=result,
            log_message=log_message,
        )
