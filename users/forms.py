from typing import Any, Optional

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mailer.models import Message
from nitrorss.base.mixins import HideColonFormMixin
from nitrorss.utils.url import get_full_url
from users.tokens import PasswordResetTokenGenerator

from .models import User


class LoginForm(HideColonFormMixin, forms.ModelForm):
    error_messages = {
        "invalid_credentials": _(
            "Please enter a correct email and password. Note that both fields may be case-sensitive."
        ),
        "user_inactive": _("This account is inactive."),
    }

    class Meta:
        model = User
        fields = ("email", "password")
        widgets = {"password": forms.PasswordInput()}

    def __init__(self, request: Optional[HttpRequest] = None, *args: Any, **kwargs: Any) -> None:
        self.request = request
        self.user_cache: Optional[User] = None

        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_credentials_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_invalid_credentials_error(self) -> ValidationError:
        return ValidationError(
            self.error_messages["invalid_credentials"],
            code="invalid_credentials",
        )

    def confirm_login_allowed(self, user: User) -> None:
        if not user.is_active:
            raise ValidationError(self.error_messages["user_inactive"], code="user_inactive")

    def get_user(self) -> Optional[User]:
        return self.user_cache


class RegisterForm(HideColonFormMixin, forms.ModelForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
    }

    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")
        widgets = {"password": forms.PasswordInput()}

    def clean_confirm_password(self) -> None:
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("confirm_password")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )


class ResetPasswordForm(HideColonFormMixin, forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def send_password_reset_email(self, user: User) -> None:
        password_reset_token = PasswordResetTokenGenerator.make_token(user=user)
        reset_url = get_full_url(reverse("users:reset-password-confirm", kwargs={"token": password_reset_token}))

        db_msg = Message.make(
            subject="Reset your password",
            text_content=f"Click here to reset your password: {reset_url}",
            recipients=[user.email],
            priority=Message.Priorities.HIGH,
        )
        db_msg.save()

    def get_user_from_email(self, email: str) -> User:
        """
        Given an email, return matching user who should receive a reset.
        """
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return None

        return user

    def save(self) -> None:
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        email = self.cleaned_data["email"]
        user = self.get_user_from_email(email)
        self.send_password_reset_email(user)


class ResetPasswordConfirmForm(HideColonFormMixin, forms.Form):
    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
    }

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self) -> None:
        password = self.cleaned_data.get("password")
        password_validation.validate_password(password, self.user)
        return password

    def clean_confirm_password(self) -> None:
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("confirm_password")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

    def save(self, commit: bool = True, *args: Any, **kwargs: Any) -> None:
        password = self.cleaned_data["password"]
        self.user.set_password(password)
        if commit:
            self.user.save(update_fields=["password"])
        return self.user


class PersonalInformationForm(HideColonFormMixin, forms.ModelForm):
    email = forms.EmailField(label=_("Email address"), disabled=True, required=False)

    class Meta:
        model = User
        fields = ("name", "email")


class EmailPreferencesForm(HideColonFormMixin, forms.Form):
    pass
