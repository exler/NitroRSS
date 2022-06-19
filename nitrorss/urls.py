from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import IndexView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("", IndexView.as_view(), name="index"),
    path("subscriptions/", include("subscriptions.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
