from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView

from .forms import AddSubscriptionForm, UpdateSubscriptionForm
from .models import Subscription


class SubscriptionsView(LoginRequiredMixin, ListView):
    template_name = "subscriptions/subscriptions.html"

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(created_by=self.request.user)


class AddSubscriptionView(LoginRequiredMixin, CreateView):
    form_class = AddSubscriptionForm
    template_name = "subscriptions/add_subscription.html"

    def get_success_url(self) -> str:
        return reverse("subscriptions:list-subscriptions")

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs


class ManageSubscriptionView(LoginRequiredMixin, UpdateView):
    form_class = UpdateSubscriptionForm
