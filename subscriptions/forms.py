from typing import Any, Optional

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from feeds.models import Feed
from nitrorss.base.mixins import HideColonFormMixin

from .models import Subscription

User = get_user_model()


class AddSubscriptionForm(HideColonFormMixin, forms.ModelForm):
    url = forms.CharField(label="URL", widget=forms.TextInput(attrs={"placeholder": "https://"}))

    class Meta:
        model = Subscription
        fields = ("url", "target_email", "schedule")
        widgets = {"target_email": forms.TextInput(attrs={"placeholder": _("Email address")})}

    def __init__(self, user: Optional[User] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.user = user
        if self.user:
            self.fields["target_email"].required = False

    def clean_url(self) -> str:
        return self.cleaned_data["url"].lower()

    def save(self, *args: Any, **kwargs: Any) -> Subscription:
        self.instance.feed = Feed.objects.get(url=self.cleaned_data["url"])
        if self.user:
            self.instance.created_by = self.user
            self.instance.target_email = self.user.email
        return super().save(*args, **kwargs)


class UpdateSubscriptionForm(HideColonFormMixin, forms.ModelForm):
    feed_url = forms.URLField(disabled=True, required=False)
    feed_title = forms.CharField(disabled=True, required=False)
    feed_description = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), disabled=True, required=False)
    feed_last_update = forms.DateField(disabled=True, required=False)
    subscription_added = forms.DateField(disabled=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["feed_url"].initial = self.instance.feed.url
            self.fields["feed_title"].initial = self.instance.feed.title
            self.fields["feed_description"].initial = self.instance.feed.description
            self.fields["feed_last_update"].initial = (
                self.instance.feed.latest_entry.date_published if self.instance.feed.latest_entry else None
            )
            self.fields["subscription_added"].initial = self.instance.created_at

    class Meta:
        model = Subscription
        fields = (
            "feed_url",
            "feed_title",
            "feed_description",
            "feed_last_update",
            "subscription_added",
            "schedule",
            "is_active",
        )
