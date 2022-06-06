from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _
from feeds.models import Feed

from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    url = forms.CharField(label="URL", widget=forms.TextInput(attrs={"placeholder": "https://"}))

    class Meta:
        model = Subscription
        fields = ("url", "target_email", "schedule")
        widgets = {"target_email": forms.TextInput(attrs={"placeholder": _("Email address")})}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["label_suffix"] = ""
        super().__init__(*args, **kwargs)

    def clean_url(self) -> str:
        return self.cleaned_data["url"].lower()

    def save(self, *args: Any, **kwargs: Any) -> Subscription:
        self.instance.feed = Feed.objects.get_or_create(
            url=self.cleaned_data["url"],
            defaults={"title": "Test"},
        )[0]
        return super().save(*args, **kwargs)
