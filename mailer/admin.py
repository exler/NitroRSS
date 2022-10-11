from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import URLPattern, path, reverse

from mailer.forms import SendTestEmailForm
from mailer.models import Message, MessageLog


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    change_list_template = "mailer/admin/changelist.html"

    exclude = ["message_data"]
    readonly_fields = ["subject", "recipients"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "send-test-email/",
                self.admin_site.admin_view(self.send_test_email),
                name="send_test_email",
            ),
        ]
        return custom_urls + urls

    def send_test_email(self, request: HttpRequest) -> None:
        opts = self.model._meta
        app_label = opts.app_label
        model_name = opts.model_name

        def render_page() -> HttpResponse:
            request.current_app = self.admin_site.name
            return render(
                request,
                "mailer/admin/send_test_email.html",
                context={
                    "opts": opts,
                    "app_label": app_label,
                    "form": form,
                },
            )

        if request.method == "GET":
            form = SendTestEmailForm()
            return render_page()
        else:
            form = SendTestEmailForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, level=messages.SUCCESS, message="Test email has been sent.")
                return redirect(reverse("admin:%s_%s_changelist" % (app_label, model_name)))
            else:
                return render_page()


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    exclude = ["message_data"]
    readonly_fields = ["subject", "recipients"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
