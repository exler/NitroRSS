import os

from django.conf import settings


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
