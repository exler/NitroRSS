from typing import Sequence

from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

from mailer.models import Message


class DatabaseBackend(BaseEmailBackend):
    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        messages = Message.objects.bulk_create([Message(email=email) for email in email_messages])
        return len(messages)
