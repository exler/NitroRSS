from celery.schedules import crontab

BEAT_SCHEDULES = {
    "check-feeds-for-new-entries": {
        "task": "feeds.tasks.check_feeds_for_new_entries",
        "schedule": crontab(minute="*/5"),
    },
    "clean-old-entries": {
        "task": "feeds.tasks.clean_old_entries",
        "schedule": crontab(hour="2", minute="30"),
    },
    "notify-subscriptions": {
        "task": "subscriptions.tasks.notify_subscriptions",
        "schedule": crontab(minute="*/5"),
    },
    "send-mail": {
        "task": "mailer.tasks.send_mail",
        "schedule": crontab(minute="*/2"),
    },
    "retry-deferred": {
        "task": "mailer.tasks.retry_deferred",
        "schedule": crontab(minute="*/30"),
    },
}
