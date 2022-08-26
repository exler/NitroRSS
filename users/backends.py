from typing import Optional

from django.contrib.auth.backends import ModelBackend

from .models import User


class EmailVerificationRequiredBackend(ModelBackend):
    def user_can_authenticate(self, user: Optional[User]) -> bool:
        email_verified = getattr(user, "email_verified", False)
        return email_verified and super().user_can_authenticate(user)
