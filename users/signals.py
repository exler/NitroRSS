from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .utils import send_verification_email


@receiver(post_save, sender=User)
def user_email_verification(instance: User, created: bool, **kwargs: Any) -> None:
    if created and not instance.email_verified:
        send_verification_email(instance)
