from django.urls import reverse
from django.views.generic import CreateView

from .forms import SubscriptionForm


class IndexView(CreateView):
    form_class = SubscriptionForm
    template_name = "subscriptions/index.html"

    def get_success_url(self) -> str:
        return reverse("subscriptions:index")
