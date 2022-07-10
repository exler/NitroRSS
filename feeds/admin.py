from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import Feed, FeedConnection, FeedEntry
from .tasks import check_feeds_for_new_entries


@admin.register(FeedEntry)
class FeedEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "date_published")


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("url", "title")
    readonly_fields = ("last_check",)

    actions = ["check_for_new_entries"]

    @admin.action(description="Check for new entries")
    def check_for_new_entries(self, request: HttpRequest, queryset: QuerySet) -> None:
        feed_ids = queryset.values_list("id", flat=True)
        msg = check_feeds_for_new_entries(feed_ids=feed_ids)
        messages.add_message(request, level=messages.SUCCESS, message=msg)


@admin.register(FeedConnection)
class FeedConnectionAdmin(admin.ModelAdmin):
    list_display = ("feed", "url")
