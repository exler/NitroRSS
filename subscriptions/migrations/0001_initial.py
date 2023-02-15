# Generated by Django 4.0.5 on 2022-07-10 19:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("feeds", "__first__"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("value", models.PositiveSmallIntegerField()),
                (
                    "units",
                    models.CharField(
                        choices=[("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days")], max_length=32
                    ),
                ),
                ("last_check", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("target_email", models.EmailField(max_length=254)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "feed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="feeds.feed"
                    ),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subscriptions",
                        to="subscriptions.schedule",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.UniqueConstraint(fields=("feed", "target_email"), name="unique_subscription_email"),
        ),
    ]
