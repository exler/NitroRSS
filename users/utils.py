from django.urls import reverse

from mailer.models import Message
from nitrorss.utils.url import get_full_url

from .models import User
from .tokens import EmailVerificationTokenGenerator


def send_verification_email(user: User) -> None:
    email_verification_token = EmailVerificationTokenGenerator.make_token(obj=user)
    verification_url = get_full_url(reverse("users:verify-email", kwargs={"token": email_verification_token}))

    db_msg = Message.make(
        subject="Verify your email",
        text_content=f"Click here to verify your email: {verification_url}",
        recipients=[user.email],
        priority=Message.Priorities.HIGH,
    )
    db_msg.save()
