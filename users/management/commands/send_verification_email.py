from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from users.models import User
from users.utils import send_verification_email


class Command(BaseCommand):
    help = "Sends an email verification to the user."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("user_email", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        user_email = options["user_email"]

        try:
            user = User.objects.get(email=user_email)
            send_verification_email(user)
            self.stdout.write(self.style.SUCCESS("Verification email sent."))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User with email %s not found." % user_email))
