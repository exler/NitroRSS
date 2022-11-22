from django.urls import reverse

from mailer.models import Message
from nitrorss.utils.emails import render_email_template_to_string
from nitrorss.utils.url import get_full_url

from .models import User
from .tokens import EmailVerificationTokenGenerator


def send_verification_email(user: User) -> None:
    email_verification_token = EmailVerificationTokenGenerator.make_token(obj=user)

    context = {
        "verification_url": get_full_url(reverse("users:verify-email", kwargs={"token": email_verification_token}))
    }
    text_message = render_email_template_to_string("users/email/verification.txt", context)
    html_message = render_email_template_to_string("users/email/verification.html", context)
    db_msg = Message.make(
        subject="Verify your email",
        text_content=text_message,
        html_content=html_message,
        recipients=[user.email],
        priority=Message.Priorities.HIGH,
    )
    db_msg.save()
