from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from feeds.models import FeedEntry

from .models import Schedule


@shared_task
def notify_subscriptions() -> None:
    schedules = Schedule.objects.filter(subscriptions__isnull=False).exclude(
        Q(subscriptions__is_active=False) | Q(subscriptions__is_deleted=True)
    )
    for schedule in schedules:
        if schedule.should_check:
            entries = (
                FeedEntry.objects.filter(date_published__gt=schedule.last_check)
                if schedule.last_check
                else FeedEntry.objects.all()
            )
            values = entries.values("feed__subscriptions", "id")
            distinct_subscriptions = values.distinct("feed__subscriptions").values_list(
                "feed__subscriptions", flat=True
            )
            for sub in distinct_subscriptions:
                # Prepare email for sending with entries for this subscription
                entries_for_sub = values.filter(feed__subscriptions=sub)
                print(f"Preparing email for subscription {sub} with {len(entries_for_sub)} entries.")

        schedule.last_check = timezone.now()
        schedule.save(update_fields=["last_check"])
