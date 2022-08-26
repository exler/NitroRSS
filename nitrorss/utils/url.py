from urllib.parse import urljoin

from django.conf import settings


def get_full_url(path: str) -> str:
    return urljoin(settings.BASE_URL, path)
