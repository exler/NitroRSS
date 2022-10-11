from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from subscriptions.forms import AddSubscriptionForm
from subscriptions.mixins import AddSubscriptionMixin


class IndexView(AddSubscriptionMixin, CreateView):
    form_class = AddSubscriptionForm
    template_name = "nitrorss/index.html"
    success_url = reverse_lazy("index")


class PrivacyView(TemplateView):
    template_name = "nitrorss/privacy.html"
