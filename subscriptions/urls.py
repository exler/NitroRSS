from django.urls import path

from .views import AddSubscriptionView, ManageSubscriptionView, SubscriptionsView

app_name = "subscriptions"
urlpatterns = [
    path("", SubscriptionsView.as_view(), name="subscriptions"),
    path("add/", AddSubscriptionView.as_view(), name="add-subscription"),
    path("<slug:slug>/", ManageSubscriptionView.as_view(), name="manage-subscription"),
]