from django.contrib import admin

from mailer.models import Message, MessageLog


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    exclude = ["message_data"]
    readonly_fields = ["subject", "recipients"]


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    exclude = ["message_data"]
    readonly_fields = ["subject", "recipients"]
