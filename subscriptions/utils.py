from django.urls import reverse

from mailer.models import Message
from nitrorss.utils.url import get_full_url

from .models import Subscription
from .tokens import ConfirmSubscriptionTokenGenerator


def send_subscription_confirmation_email(subscription: Subscription) -> None:
    confirmation_token = ConfirmSubscriptionTokenGenerator.make_token(obj=subscription)
    verification_url = get_full_url(reverse("subscriptions:confirm-subscription", kwargs={"token": confirmation_token}))

    db_msg = Message.make(
        subject="Verify your subscription",
        text_content=f"Click here to verify your subscription: {verification_url}",
        recipients=[subscription.target_email],
        priority=Message.Priorities.HIGH,
    )
    db_msg.save()
