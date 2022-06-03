# Generated by Django 4.0.5 on 2022-06-03 21:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subscriptions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscription',
            name='feed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='feeds.feed'),
        ),
    ]
