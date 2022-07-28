from django.contrib import admin

from mailer.models import Message, MessageLog


class EmailBodyMixin:
    def body(self, obj: Message | MessageLog) -> str:
        email = obj.email
        return email.body


@admin.register(Message)
class MessageAdmin(EmailBodyMixin, admin.ModelAdmin):
    exclude = ["_message_data"]
    readonly_fields = ["body"]


@admin.register(MessageLog)
class MessageLogAdmin(EmailBodyMixin, admin.ModelAdmin):
    exclude = ["_message_data"]
    readonly_fields = ["body"]
