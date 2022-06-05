from django.views.generic import CreateView

from .forms import SubscriptionForm


class IndexView(CreateView):
    form_class = SubscriptionForm
    template_name = "subscriptions/index.html"
