from django.conf import settings
from django.template.loader import get_template


def render_email_template_to_string(template_name: str, context: dict = {}) -> str:
    email_context = {
        "base_url": settings.BASE_URL,
    }
    email_context.update(context)

    template = get_template(template_name, using=None)
    return template.render(context)
