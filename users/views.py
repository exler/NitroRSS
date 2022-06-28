from typing import Any

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, FormView, RedirectView, TemplateView

from .forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"


class LoginView(FormView):
    form_class = LoginForm
    template_name = "users/login.html"

    def get_success_url(self) -> str:
        return reverse("subscriptions:list-subscriptions")

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
