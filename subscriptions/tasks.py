from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from feeds.models import FeedEntry
from mailer.models import Message

from .models import Schedule


@shared_task
def notify_subscriptions() -> None:
    notified_count = 0
    schedules = Schedule.objects.filter(subscriptions__isnull=False).exclude(
        Q(subscriptions__is_active=False) | Q(subscriptions__is_deleted=True)
    )
    for schedule in schedules:
        if schedule.should_check:
            entries = (
                FeedEntry.objects.filter(
                    feed__subscriptions__schedule_id=schedule.id, date_published__gt=schedule.last_check
                )
                if schedule.last_check
                else FeedEntry.objects.filter(
                    feed__subscriptions__schedule_id=schedule.id,
                )
            )
            values = entries.values("feed__subscriptions", "feed__subscriptions__target_email", "id")
            distinct_subscriptions = values.distinct("feed__subscriptions").values(
                "feed__subscriptions", "feed__subscriptions__target_email"
            )
            db_messages = []
            for sub in distinct_subscriptions:
                # Prepare email for sending with entries for this subscription
                entries_for_sub = values.filter(feed__subscriptions=sub["feed__subscriptions"]).values(
                    "link", "title", "description"
                )
                message = ""
                for entry in entries_for_sub:
                    message += f"Link: {entry['link']}, Title: {entry['title']}, Description: {entry['description']}\n"

                db_msg = Message.make(
                    subject="Your subscription has new entries!",
                    body=message,
                    recipients=[sub["feed__subscriptions__target_email"]],
                )
                db_messages.append(db_msg)

            messages = Message.objects.bulk_create(db_messages)
            notified_count += len(messages)

        schedule.last_check = timezone.now()
        schedule.save(update_fields=["last_check"])

    return f"Notified {notified_count} subscriptions"
