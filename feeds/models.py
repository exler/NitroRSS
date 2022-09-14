from typing import Optional

import feedparser
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from nitrorss.common.models import TimestampedModel
from nitrorss.utils.strings import HTMLCleaner, smart_truncate

from .utils import struct_time_to_datetime


class FeedEntry(models.Model):
    feed = models.ForeignKey("feeds.Feed", on_delete=models.CASCADE, related_name="entries")

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=500)

    date_published = models.DateTimeField()

    # List of authors in format "Author 1, Author 2"
    authors = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("feed entry")
        verbose_name_plural = _("feed entries")


class Feed(TimestampedModel):
    url = models.URLField(max_length=255, unique=True, db_index=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    last_check = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Feed: {self.url}"

    @property
    def latest_entry(self) -> Optional[FeedEntry]:
        return self.entries.order_by("-date_published").first()

    def get_entries(self) -> list[FeedEntry]:
        feed_entries: list[FeedEntry] = []
        entries = feedparser.parse(self.url).entries

        html_cleaner = HTMLCleaner()

        for entry in entries:
            title = entry.get("title")
            description = smart_truncate(html_cleaner.clean(entry.get("description")), 324)
            link = entry.get("link")
            authors = ", ".join([x.get("name") for x in entry.get("authors", []) if "name" in x])
            date_published = struct_time_to_datetime(entry.get("published_parsed"))

            feed_entries.append(
                FeedEntry(
                    feed=self,
                    link=link,
                    title=title,
                    description=description,
                    authors=authors,
                    date_published=date_published,
                )
            )

        return feed_entries


class FeedConnection(models.Model):
    feed = models.ForeignKey("feeds.Feed", on_delete=models.CASCADE, related_name="connections")
    url = models.URLField(max_length=255, db_index=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["feed", "url"], name="unique_feed_connection_url"),
        ]
