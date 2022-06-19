from django.urls import include, path

from .views import AccountView, LoginView, LogoutView, RegisterView

app_name = "users"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", RegisterView.as_view(), name="register"),
    path(
        "account/",
        include(
            [
                path("", AccountView.as_view(), name="account"),
            ]
        ),
    ),
]
