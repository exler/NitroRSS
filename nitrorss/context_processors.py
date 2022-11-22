from django.conf import settings
from django.http.request import HttpRequest


def base_url_processor(request: HttpRequest) -> dict:
    return {"base_url": settings.BASE_URL}
