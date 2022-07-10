from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from feeds.models import Feed


class Command(BaseCommand):
    help = "Gets feed entries for specified feed"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("feed_id", type=int)

    def handle(self, *args: Any, **options: Any) -> None:
        feed = Feed.objects.get(id=options["feed_id"])
        entries = feed.get_entries()
        for idx, entry in enumerate(entries, start=1):
            self.stdout.write(self.style.SUCCESS(f"Entry {idx}"))

            for field in ["title", "description", "link", "authors", "date_published"]:
                self.stdout.write(f"{field.title()}: {getattr(entry, field)}")

            self.stdout.write("\n")
