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
        self.instance.feed = Feed.objects.get_or_create(
            url=self.cleaned_data["url"],
            defaults={"title": "Test"},
        )[0]
        self.instance.created_by = self.user
        return super().save(*args, **kwargs)


class UpdateSubscriptionForm(HideColonFormMixin, forms.ModelForm):
    feed_url = forms.URLField()
    feed_title = forms.CharField()
    feed_description = forms.CharField(widget=forms.Textarea())
    feed_last_update = forms.DateField()
    subscription_added = forms.DateField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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
