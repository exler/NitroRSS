from django.template.loader import render_to_string
from django.urls import reverse

from mailer.models import Message
from nitrorss.utils.url import get_full_url

from .models import Subscription
from .tokens import ConfirmSubscriptionTokenGenerator


def send_subscription_confirmation_email(subscription: Subscription) -> None:
    confirmation_token = ConfirmSubscriptionTokenGenerator.make_token(obj=subscription)

    context = {
        "verification_url": get_full_url(
            reverse("subscriptions:confirm-subscription", kwargs={"token": confirmation_token})
        )
    }
    text_message = render_to_string("subscriptions/email/verification.txt", context)
    html_message = render_to_string("subscriptions/email/verification.html", context)
    db_msg = Message.make(
        subject="Verify your subscription",
        text_content=text_message,
        html_content=html_message,
        recipients=[subscription.target_email],
        priority=Message.Priorities.HIGH,
    )
    db_msg.save()
