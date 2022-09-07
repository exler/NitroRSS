from typing import Any

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, FormView, RedirectView, TemplateView

from users.tokens import EmailVerificationTokenGenerator

from .forms import (
    EmailPreferencesForm,
    LoginForm,
    PersonalInformationForm,
    RegisterForm,
    ResetPasswordConfirmForm,
    ResetPasswordForm,
)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"


class VerifyEmailView(RedirectView):
    url = reverse_lazy("users:login")

    def get(self, request: HttpRequest, token: str, *args: Any, **kwargs: Any) -> HttpResponseBase:
        user = EmailVerificationTokenGenerator.check_token(token)

        if user:
            if user.email_verified:
                messages.add_message(request, messages.WARNING, "Your email is already verified.")
            else:
                user.email_verified = True
                user.save(update_fields=["email_verified"])
                messages.add_message(request, messages.SUCCESS, "Your email has been verified. You can now sign in.")

            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied("Invalid token")


class ResetPasswordView(FormView):
    template_name = "users/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("users:reset-password-requested")

    def form_valid(self, form: ResetPasswordForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)


class ResetPasswordRequestedView(TemplateView):
    template_name = "users/reset_password_requested.html"


class ResetPasswordConfirmView(FormView):
    template_name = "users/reset_password_confirm.html"
    form_class = ResetPasswordConfirmForm
    success_url = reverse_lazy("users:login")

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["token"] = self.kwargs["token"]
        return context

    def form_valid(self, form: ResetPasswordConfirmForm) -> HttpResponse:
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Your password has been reset. You can now sign in.")
        return super().form_valid(form)


class LoginView(FormView):
    form_class = LoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy("subscriptions:list-subscriptions")

    def form_valid(self, form: LoginForm) -> HttpResponse:
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class LogoutView(RedirectView):
    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        auth_logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        return reverse("index")


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "users/account.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["information_form"] = PersonalInformationForm(
            prefix="information",
            initial={
                "name": self.request.user.name,
                "email": self.request.user.email,
            },
        )
        context["preferences_form"] = EmailPreferencesForm(prefix="preferences")
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """
        Handle request with multiple forms.
        """
        user = request.user

        information_form = PersonalInformationForm(request.POST, instance=user, prefix="information")
        preferences_form = EmailPreferencesForm(request.POST, prefix="preferences")

        if information_form.is_valid():
            information_form.save()

        if preferences_form.is_valid():
            pass
            # preferences_form.save()

        return self.get(request, *args, **kwargs)
