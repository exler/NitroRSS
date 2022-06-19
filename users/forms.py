from typing import Any, Optional

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from nitrorss.base.mixins import HideColonFormMixin

from .models import User


class LoginForm(HideColonFormMixin, forms.ModelForm):
    error_messages = {
        "invalid_credentials": _(
            "Please enter a correct username and password. Note that both fields may be case-sensitive."
        ),
        "user_inactive": _("This account is inactive."),
    }

    class Meta:
        model = User
        fields = ("username", "password")
        widgets = {"password": forms.PasswordInput()}

    def __init__(self, request: Optional[HttpRequest] = None, *args: Any, **kwargs: Any) -> None:
        self.request = request
        self.user_cache: Optional[User] = None

        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
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
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "password", "confirm_password")
        widgets = {"password": forms.PasswordInput()}

    def clean_confirm_password(self) -> None:
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("confirm_password")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
