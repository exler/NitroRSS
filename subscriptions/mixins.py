from typing import Any, Optional

from django.contrib import messages
from django.db import IntegrityError
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase

from feeds.models import Feed
from feeds.rss import find_feeds
from subscriptions.models import Subscription


class AddSubscriptionMixin:
    """
    Mixin for working with the AddSubscriptionForm.
    """

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
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
                # Feed is found, so we can create a subscription
                self.form_valid(form)
                # Make new response that will trigger HTMX to redirect
                response = HttpResponse()
                response["HX-Redirect"] = self.get_success_url()
                messages.add_message(request, messages.SUCCESS, f"You have subscribed to '{form.cleaned_data['url']}'")
                return response
            except Feed.DoesNotExist:
                # Feed is not found, so we can search for possible feeds and display them to user
                feeds = find_feeds(url)
                if not feeds:
                    messages.add_message(request, messages.ERROR, "No feeds found.")
                    return self.render_to_response(self.get_context_data())

                return self.render_to_response(self.get_context_data(feeds=feeds))
            except IntegrityError:
                form.add_error("url", "This feed is already subscribed.")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)
