# Generated by Django 4.0.7 on 2022-09-05 19:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailer", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="messagelog",
            name="priority",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Deferred"), (10, "Low"), (20, "Medium"), (30, "High")], default=20
            ),
            preserve_default=False,
        ),
    ]
