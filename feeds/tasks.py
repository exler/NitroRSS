from typing import Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from feeds.models import Feed, FeedEntry


def check_feeds_for_new_entries(feed_ids: Optional[list[int]] = None) -> str:
    now = timezone.now()
    entry_counter = 0

    with transaction.atomic():
        if feed_ids:
            feed_objs = Feed.objects.select_for_update().filter(id__in=feed_ids)
        else:
            # Check only feeds with active subscriptions
            feed_objs = Feed.objects.select_for_update().exclude(
                Q(subscriptions__isnull=True) | Q(subscriptions__is_active=False)
            )

        for feed_obj in feed_objs:
            entries = feed_obj.get_entries()

            for entry_index, entry in enumerate(entries, start=1):
                if entry.date_published <= feed_obj.last_check:
                    entry_index -= 1
                    break

            if entry_index > 0:
                entries = entries[:entry_index]
                FeedEntry.objects.bulk_create(entries)
                entry_counter += len(entries)

            feed_obj.last_check = now

        Feed.objects.bulk_update(feed_objs, ["last_check"])

    if entry_counter > 0:
        return f"Created {entry_counter} new entries."

    return "No new entries."


def clean_old_entries() -> str:
    entries_deleted = FeedEntry.objects.filter(
        date_published__lt=timezone.now() - timezone.timedelta(days=30)
    ).delete()[0]

    return f"Deleted {entries_deleted} old entries."
