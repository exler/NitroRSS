import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nitrorss.settings")

app = Celery("nitrorss")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self) -> None:  # noqa
    print(f"Request: {self.request}")
