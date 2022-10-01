import os

from django.conf import settings
from django.template.loader import get_template


def get_email_templates() -> list[str]:
    templates = []
    app_dirs = [f.path for f in os.scandir(settings.BASE_DIR) if f.is_dir() and f.name in settings.INSTALLED_APPS]
    for app_dir in app_dirs:
        app_name = os.path.basename(app_dir)
        email_dir = os.path.join(app_dir, "templates", app_name, "email")
        if os.path.exists(email_dir):
            for f in os.scandir(email_dir):
                if f.name.endswith((".html", ".txt")):
                    templates.append(f"{app_name}/email/{f.name}")
    return templates


def render_email_template_to_string(template_name: str, context: dict = {}) -> str:
    email_context = {
        "base_url": settings.BASE_URL,
    }
    email_context.update(context)

    template = get_template(template_name, using=None)
    return template.render(context)
