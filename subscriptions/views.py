from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    RedirectView,
    UpdateView,
)

from subscriptions.mixins import AddSubscriptionMixin
from subscriptions.tokens import ConfirmSubscriptionTokenGenerator

from .forms import AddSubscriptionForm, UpdateSubscriptionForm
from .models import Subscription


class SubscriptionsView(LoginRequiredMixin, ListView):
    template_name = "subscriptions/subscriptions.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(created_by=self.request.user)


class AddSubscriptionView(AddSubscriptionMixin, LoginRequiredMixin, CreateView):
    form_class = AddSubscriptionForm
    template_name = "subscriptions/add_subscription.html"
    success_url = reverse_lazy("subscriptions:list-subscriptions")


class ManageSubscriptionView(LoginRequiredMixin, UpdateView):
    form_class = UpdateSubscriptionForm
    template_name = "subscriptions/manage_subscription.html"
    success_url = reverse_lazy("subscriptions:list-subscriptions")

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(created_by=self.request.user)


class DeleteSubscriptionView(LoginRequiredMixin, DeleteView):
    model = Subscription
    template_name = "subscriptions/confirm_delete.html"
    success_url = reverse_lazy("subscriptions:list-subscriptions")


class ConfirmSubscriptionView(RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        if self.request.user.is_authenticated:
            return reverse("subscriptions:list-subscriptions")
        else:
            return reverse("index")

    def get(self, request: HttpRequest, token: str, *args: Any, **kwargs: Any) -> HttpResponseBase:
        subscription = ConfirmSubscriptionTokenGenerator.check_token(token)

        if subscription:
            if subscription.confirmed:
                messages.add_message(request, messages.WARNING, "Your subscription is already verified.")
            else:
                subscription.confirmed = True
                subscription.save(update_fields=["confirmed"])
                messages.add_message(request, messages.SUCCESS, "Your subscription has been confirmed.")

            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied("Invalid token")


class UnsubscribeView(RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        if self.request.user.is_authenticated:
            return reverse("subscriptions:list-subscriptions")
        else:
            return reverse("index")

    def get(self, request: HttpRequest, token: str, *args: Any, **kwargs: Any) -> HttpResponseBase:
        try:
            subscription = Subscription.objects.get(unsubscribe_token=token)
            subscription.delete()
            messages.add_message(request, messages.SUCCESS, "You have been unsubscribed from this feed.")
            return super().get(request, *args, **kwargs)
        except Subscription.DoesNotExist:
            raise PermissionDenied("Invalid token")
