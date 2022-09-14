from typing import Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    RedirectView,
    UpdateView,
)

from feeds.models import Feed
from feeds.rss import find_feeds
from subscriptions.tokens import ConfirmSubscriptionTokenGenerator

from .forms import AddSubscriptionForm, UpdateSubscriptionForm
from .models import Subscription


class SubscriptionsView(LoginRequiredMixin, ListView):
    template_name = "subscriptions/subscriptions.html"

    def get_queryset(self) -> QuerySet[Subscription]:
        return Subscription.objects.filter(created_by=self.request.user)


class AddSubscriptionView(LoginRequiredMixin, CreateView):
    form_class = AddSubscriptionForm
    template_name = "subscriptions/add_subscription.html"
    success_url = reverse_lazy("subscriptions:list-subscriptions")

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """
        Instantiate a form instance with the passed POST variables and then check if it's valid.

        Check if a feed with given URL already exists.
        If there is no such feed in DB, then search for possible feeds with `find_feeds`.
        """
        self.object: Optional[Subscription] = None
        form = self.get_form()
        if form.is_valid():
            url = form.cleaned_data["url"]
            try:
                Feed.objects.get(url=url)
                self.form_valid(form)
                # Make new response that will trigger HTMX to redirect
                response = HttpResponse()
                response["HX-Redirect"] = self.get_success_url()
                return response
            except Feed.DoesNotExist:
                feeds = find_feeds(url)
                return self.render_to_response(self.get_context_data(feeds=feeds))
            except IntegrityError:
                form.add_error("url", "This feed is already subscribed.")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


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
