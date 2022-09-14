from django.urls import path

from .views import (
    AddSubscriptionView,
    ConfirmSubscriptionView,
    DeleteSubscriptionView,
    ManageSubscriptionView,
    SubscriptionsView,
    UnsubscribeView,
)

app_name = "subscriptions"
urlpatterns = [
    path("", SubscriptionsView.as_view(), name="list-subscriptions"),
    path("add/", AddSubscriptionView.as_view(), name="add-subscription"),
    path("<int:pk>/", ManageSubscriptionView.as_view(), name="manage-subscription"),
    path("<int:pk>/delete/", DeleteSubscriptionView.as_view(), name="delete-subscription"),
    path("confirm/<str:token>/", ConfirmSubscriptionView.as_view(), name="confirm-subscription"),
    path("unsubscribe/<str:token>/", UnsubscribeView.as_view(), name="unsubscribe"),
]
