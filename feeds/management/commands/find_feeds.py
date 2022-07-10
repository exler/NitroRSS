from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from feeds.rss import find_feeds


class Command(BaseCommand):
    help = "Finds RSS and Atom feeds for specified URLs"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("url", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        url = options["url"]

        feeds = find_feeds(url)
        for feed in feeds:
            self.stdout.write(self.style.SUCCESS('Found feed "%s" at %s' % (feed.title or "Unknown", feed.url)))
