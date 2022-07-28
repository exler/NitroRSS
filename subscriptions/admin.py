from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.urls import URLPattern, path, reverse

from .models import Schedule, Subscription
from .tasks import notify_subscriptions


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    change_list_template = "subscriptions/admin/changelist.html"

    list_display = ("feed", "target_email", "schedule")

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "notify-subscriptions/",
                self.admin_site.admin_view(self.notify_subscriptions),
                name="notify_subscriptions",
            ),
        ]
        return custom_urls + urls

    def notify_subscriptions(self, request: HttpRequest) -> None:
        msg = notify_subscriptions()
        messages.add_message(request, level=messages.SUCCESS, message=msg)
        return redirect(reverse("admin:%s_%s_changelist" % (self.model._meta.app_label, self.model._meta.model_name)))
