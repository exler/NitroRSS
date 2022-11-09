from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class AuthenticatedTestCase(TestCase):
    def _pre_setup(self) -> None:
        super()._pre_setup()

        self.user = User.objects.create_user(  # nosec
            email="skarlet@nitrorss.com",
            password="password",
            email_verified=True,
        )
        self.client.force_login(self.user)
