import secrets

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from feeds.models import Feed
from nitrorss.common.models import TimestampedModel
from nitrorss.common.validators import DisposableEmailBlacklistValidator


class Schedule(models.Model):
    class Units(models.TextChoices):
        MINUTES = "minutes", _("Minutes")
        HOURS = "hours", _("Hours")
        DAYS = "days", _("Days")

    name = models.CharField(max_length=64)
    value = models.PositiveSmallIntegerField()
    units = models.CharField(max_length=32, choices=Units.choices)

    last_check = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def should_check(self) -> timezone.timedelta:
        return (
            self.last_check <= timezone.now() - timezone.timedelta(**{self.units: self.value})
            if self.last_check
            else True
        )


class SubscriptionQuerySet(models.QuerySet):
    def active(self) -> models.QuerySet:
        return self.filter(is_active=True)


def get_unsubscribe_token() -> str:
    return secrets.token_urlsafe(32)


class Subscription(TimestampedModel):
    feed = models.ForeignKey(Feed, on_delete=models.PROTECT, related_name="subscriptions")
    target_email = models.EmailField(validators=[DisposableEmailBlacklistValidator()])

    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, related_name="subscriptions")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions", null=True, blank=True
    )

    # Subscriptions can be deactivated by the user
    is_active = models.BooleanField(default=True)
    # Whether the user can confirmed the email address for this subscription
    confirmed = models.BooleanField(default=False)

    unsubscribe_token = models.CharField(max_length=64, unique=True, default=get_unsubscribe_token)

    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        constraints = [
            UniqueConstraint(fields=["feed", "target_email"], name="unique_subscription_email"),
        ]
