from django.urls import include, path

from .views import (
    AccountView,
    LoginView,
    LogoutView,
    RegisterView,
    ResetPasswordConfirmView,
    ResetPasswordRequestedView,
    ResetPasswordView,
    VerifyEmailView,
)

app_name = "users"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", RegisterView.as_view(), name="register"),
    path("verify/<str:token>/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resetpassword/",
        include(
            [
                path("", ResetPasswordView.as_view(), name="reset-password"),
                path("requested/", ResetPasswordRequestedView.as_view(), name="reset-password-requested"),
                path("<str:token>/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),
            ]
        ),
    ),
    path(
        "account/",
        include(
            [
                path("", AccountView.as_view(), name="account"),
            ]
        ),
    ),
]
