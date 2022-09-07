from typing import Any

from django.core.management.base import BaseCommand

from mailer.engine import send_all


class Command(BaseCommand):
    help = "Calls the send_all function"

    def handle(self, *args: Any, **options: Any) -> None:
        send_all()
        self.stdout.write(self.style.SUCCESS("Sent all messages"))
