from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription
from .utils import send_subscription_confirmation_email


@receiver(post_save, sender=Subscription)
def confirm_subscription(instance: Subscription, created: bool, **kwargs: Any) -> None:
    if created and not instance.confirmed:
        send_subscription_confirmation_email(instance)
