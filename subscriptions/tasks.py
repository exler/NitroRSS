from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from feeds.models import FeedEntry
from mailer.models import Message
from nitrorss.utils.emails import render_email_template_to_string
from nitrorss.utils.url import get_full_url

from .models import Schedule


def notify_subscriptions() -> None:
    notified_count = 0
    schedules = Schedule.objects.filter(subscriptions__isnull=False).exclude(
        Q(subscriptions__is_active=False) | Q(subscriptions__confirmed=False)
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
                "feed__title",
                "feed__subscriptions",
                "feed__subscriptions__target_email",
                "feed__subscriptions__unsubscribe_token",
            )
            db_messages = []
            for sub in distinct_subscriptions:
                # Prepare email for sending with entries for this subscription
                entries_for_sub = values.filter(feed__subscriptions=sub["feed__subscriptions"]).values(
                    "link", "title", "description"
                )
                context = {
                    "feed_title": sub["feed__title"],
                    "entries": entries_for_sub,
                    "unsubscribe_url": get_full_url(
                        reverse(
                            "subscriptions:unsubscribe", kwargs={"token": sub["feed__subscriptions__unsubscribe_token"]}
                        )
                    ),
                }
                text_message = render_email_template_to_string("subscriptions/email/digest.txt", context)
                html_message = render_email_template_to_string("subscriptions/email/digest.html", context)
                db_msg = Message.make(
                    subject="Your subscription has new entries!",
                    text_content=text_message,
                    html_content=html_message,
                    recipients=[sub["feed__subscriptions__target_email"]],
                )
                db_messages.append(db_msg)

            messages = Message.objects.bulk_create(db_messages)
            notified_count += len(messages)

        schedule.last_check = timezone.now()
        schedule.save(update_fields=["last_check"])

    return f"Notified {notified_count} subscriptions"
