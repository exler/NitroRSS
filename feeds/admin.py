from django.contrib import admin

from .models import Feed, FeedConnection


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("url", "title")


@admin.register(FeedConnection)
class FeedConnectionAdmin(admin.ModelAdmin):
    list_display = ("feed", "url")
