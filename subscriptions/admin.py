from django.contrib import admin

from .models import Schedule, Subscription


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("feed", "target_email", "schedule")
