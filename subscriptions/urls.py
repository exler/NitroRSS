from django.urls import path

from .views import IndexView

app_name = "subscriptions"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]
