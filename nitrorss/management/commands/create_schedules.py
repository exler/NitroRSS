from typing import Any

from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django_q.tasks import schedule


class Command(BaseCommand):
    help = "Creates Django Q schedules"

    def handle(self, *args: Any, **options: Any) -> None:
        if not Schedule.objects.exists():
            schedule("feeds.tasks.check_feeds_for_new_entries", schedule_type="C", cron="*/5 * * * *")
            schedule("feeds.tasks.clean_old_entries", schedule_type="C", cron="30 2 * * *")
            schedule("mailer.tasks.send_mail", schedule_type="C", cron="*/2 * * * *")
            schedule("mailer.tasks.retry_deferred", schedule_type="C", cron="*/30 * * * *")
            schedule("subscriptions.tasks.notify_subscriptions", schedule_type="C", cron="*/5 * * * *")
            self.stdout.write(self.style.SUCCESS("Successfully created schedules"))
        self.stdout.write(self.style.WARNING("Schedules already exist"))
