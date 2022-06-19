from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import CreateView, ListView, UpdateView

from .forms import AddSubscriptionForm, UpdateSubscriptionForm
from .models import Subscription


class SubscriptionsView(LoginRequiredMixin, ListView):
    template_name = "subscriptions/subscriptions.html"

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(created_by=self.request.user)


class AddSubscriptionView(LoginRequiredMixin, CreateView):
    form_class = AddSubscriptionForm


class ManageSubscriptionView(LoginRequiredMixin, UpdateView):
    form_class = UpdateSubscriptionForm
