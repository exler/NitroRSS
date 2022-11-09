from urllib.parse import urljoin

import factory
from django.template.defaultfilters import slugify
from django.utils import timezone

from .models import Feed, FeedEntry


class FeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed
        django_get_or_create = ("url",)

    url = "http://example.com/feed"
    title = "Example Feed"
    description = "This is an example feed"


class FeedEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeedEntry

    feed = factory.SubFactory(FeedFactory)

    title = factory.Faker("sentence", nb_words=8)
    description = factory.Faker("text", max_nb_chars=324)
    link = factory.LazyAttribute(lambda o: urljoin(o.feed.url, slugify(o.title)))

    date_published = factory.LazyFunction(timezone.now)
