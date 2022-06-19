from django.urls import reverse
from django.views.generic import CreateView

from subscriptions.forms import AddSubscriptionForm


class IndexView(CreateView):
    form_class = AddSubscriptionForm
    template_name = "nitrorss/index.html"

    def get_success_url(self) -> str:
        return reverse("index")
