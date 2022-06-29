from django.db import models
from django.db.models import UniqueConstraint

from nitrorss.common.models import TimestampedModel


class Feed(TimestampedModel):
    url = models.URLField(max_length=255, unique=True, db_index=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    last_check = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Feed - {self.url}"


class FeedConnection(TimestampedModel):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="connections")
    url = models.URLField(max_length=255, db_index=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["feed", "url"], name="unique_feed_connection_url"),
        ]
