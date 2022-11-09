import factory

from feeds.factories import FeedFactory

from .models import Schedule, Subscription


class ScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Schedule
        django_get_or_create = ("value", "units")

    name = "Realtime"
    value = 5
    units = Schedule.Units.MINUTES


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription
        django_get_or_create = ("feed", "target_email")

    feed = factory.SubFactory(FeedFactory)
    target_email = factory.Faker("email")

    confirmed = True

    schedule = factory.SubFactory(ScheduleFactory)
