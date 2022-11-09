import re
from urllib.parse import urlparse

from django.test import TestCase
from django.urls import reverse

from mailer.models import Message
from users.models import User
from users.views import ResetPasswordConfirmView


class TestUserAuthentication(TestCase):
    LOGIN_URL = reverse("users:login")
    LOGOUT_URL = reverse("users:logout")
    REGISTER_URL = reverse("users:register")
    RESET_PASSWORD_URL = reverse("users:reset-password")

    def test_user_can_register(self) -> None:
        response = self.client.post(
            self.REGISTER_URL,
            data={"email": "user@example.com", "password": "password", "confirm_password": "password"},
        )
        self.assertRedirects(response, self.LOGIN_URL, status_code=302, target_status_code=200)

        user = User.objects.get(email="user@example.com")
        self.assertTrue(user.check_password("password"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.email_verified)

    def test_user_can_verify_email(self) -> None:
        response = self.client.post(
            self.REGISTER_URL,
            data={"email": "user@example.com", "password": "password", "confirm_password": "password"},
        )
        self.assertEqual(response.status_code, 302)

        message = Message.objects.order_by("-id").first()
        self.assertIsNotNone(message)

        self.assertListEqual(message.recipients, ["user@example.com"])

        url = re.search(r"(?P<url>https?://[^\s]+)", message.email.body)
        self.assertIsNotNone(url, msg="No URL found in email body")

        url = urlparse(url.group("url")).path
        response = self.client.get(url)
        self.assertRedirects(response, self.LOGIN_URL, status_code=302, target_status_code=200)
        self.assertTrue(User.objects.get(email="user@example.com").email_verified)

    def test_user_can_login(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password", email_verified=True)  # nosec
        response = self.client.post(self.LOGIN_URL, data={"email": user.email, "password": "password"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("index"))
        self.assertContains(response, "Sign out")

    def test_user_can_logout(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password", email_verified=True)  # nosec
        self.client.force_login(user)

        response = self.client.get(reverse("index"))
        self.assertContains(response, "Sign out")

        response = self.client.get(self.LOGOUT_URL)
        self.assertRedirects(response, reverse("index"), status_code=302, target_status_code=200)

        response = self.client.get(reverse("index"))
        self.assertContains(response, "Sign in")

    def test_unverified_user_cannot_reset_password(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password")  # nosec
        response = self.client.post(self.RESET_PASSWORD_URL, data={"email": user.email})
        self.assertContains(response, "No user with this email address exists.")

    def test_user_can_reset_password(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password", email_verified=True)  # nosec

        response = self.client.post(self.RESET_PASSWORD_URL, data={"email": user.email})
        self.assertRedirects(
            response, reverse("users:reset-password-requested"), status_code=302, target_status_code=200
        )

        message = Message.objects.order_by("-id").first()
        self.assertIsNotNone(message)

        self.assertListEqual(message.recipients, ["user@example.com"])

        url = re.search(r"(?P<url>https?://[^\s]+)", message.email.body)
        self.assertIsNotNone(url, msg="No URL found in email body")

        url = urlparse(url.group("url")).path
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("users:reset-password-confirm", kwargs={"token": ResetPasswordConfirmView.reset_url_token}),
            status_code=302,
            target_status_code=200,
        )

        response = self.client.post(
            reverse("users:reset-password-confirm", kwargs={"token": ResetPasswordConfirmView.reset_url_token}),
            data={"password": "new_password", "confirm_password": "new_password"},
        )
        self.assertRedirects(response, self.LOGIN_URL, status_code=302, target_status_code=200)

        user.refresh_from_db()
        self.assertTrue(user.check_password("new_password"))
