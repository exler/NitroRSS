from django.db import models

from nitrorss.common.models import TimestampedModel


class Feed(TimestampedModel):
    url = models.URLField(max_length=255, unique=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    last_check = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"
