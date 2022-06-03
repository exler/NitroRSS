from django.conf import settings
from django.db import models
from feeds.models import Feed
from nitrorss.common.models import TimestampedModel


class Subscription(TimestampedModel):
    class Schedules(models.IntegerChoices):
        REALTIME = 1
        EVERY_2_HOURS = 2
        EVERY_4_HOURS = 3
        EVERY_6_HOURS = 4
        EVERY_12_HOURS = 5
        DAILY = 6

    feed = models.ForeignKey(Feed, on_delete=models.PROTECT, related_name="subscriptions")
    target_email = models.EmailField()

    schedule = models.SmallIntegerField(choices=Schedules.choices)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions", null=True, blank=True
    )

    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
