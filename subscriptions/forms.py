from django import forms

from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    url = forms.URLField()

    class Meta:
        model = Subscription
        fields = ("url", "target_email", "schedule")
