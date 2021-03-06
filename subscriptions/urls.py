from django.urls import path

from .views import (
    AddSubscriptionView,
    DeleteSubscriptionView,
    ManageSubscriptionView,
    SubscriptionsView,
)

app_name = "subscriptions"
urlpatterns = [
    path("", SubscriptionsView.as_view(), name="list-subscriptions"),
    path("add/", AddSubscriptionView.as_view(), name="add-subscription"),
    path("<int:pk>/", ManageSubscriptionView.as_view(), name="manage-subscription"),
    path("<int:pk>/delete/", DeleteSubscriptionView.as_view(), name="delete-subscription"),
]
