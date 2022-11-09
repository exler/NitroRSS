from django.test import TestCase
from freezegun import freeze_time

from feeds.factories import FeedEntryFactory, FeedFactory
from mailer.models import Message
from subscriptions.factories import ScheduleFactory, SubscriptionFactory
from subscriptions.models import Schedule
from subscriptions.tasks import notify_subscriptions


class TestSubscriptionNotifications(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.schedule = ScheduleFactory(name="Realtime", value=5, units=Schedule.Units.MINUTES)
        cls.feed = FeedFactory()

    def test_single_user_notification(self) -> None:
        subscription = SubscriptionFactory(feed=self.feed, schedule=self.schedule, target_email="user1@example.com")

        with freeze_time("2022-10-10"):
            entries = [FeedEntryFactory(feed=self.feed) for _ in range(2)]

        notify_subscriptions()

        message = Message.objects.order_by("-id").first()
        self.assertIsNotNone(message)
        self.assertListEqual(message.recipients, [subscription.target_email])
        self.assertEqual(message.subject, "Your subscription has new entries!")

        for entry in entries:
            self.assertIn(entry.title, message.email.body)
            self.assertIn(entry.link, message.email.body)

        self.assertEqual(message.email.body.count("Post title"), 2)

    def test_multiple_users_notifications(self) -> None:
        mails = ["user1@example.com", "user2@example.com"]
        [
            SubscriptionFactory(feed=self.feed, schedule=self.schedule, target_email=mails[0]),
            SubscriptionFactory(feed=self.feed, schedule=self.schedule, target_email=mails[1]),
        ]

        with freeze_time("2022-10-10"):
            entries = [FeedEntryFactory(feed=self.feed) for _ in range(2)]

        notify_subscriptions()

        messages = Message.objects.order_by("-id")[:2]
        self.assertEqual(messages.count(), 2)

        for message in messages:
            self.assertTrue(message.recipients[0] in mails)
            mails.remove(message.recipients[0])

            self.assertEqual(message.subject, "Your subscription has new entries!")
            for entry in entries:
                self.assertIn(entry.title, message.email.body)
                self.assertIn(entry.link, message.email.body)

            self.assertEqual(message.email.body.count("Post title"), 2)
