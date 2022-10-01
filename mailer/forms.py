from typing import Any

from django import forms

from mailer.models import Message
from nitrorss.utils.emails import get_email_templates, render_email_template_to_string


class SendTestEmailForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField()
    template = forms.ChoiceField()
    context = forms.JSONField(required=False, initial={})

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["template"].choices = [(template, template) for template in get_email_templates()]

    def save(self) -> None:
        recipient = self.cleaned_data["email"]
        subject = self.cleaned_data["subject"]
        template_name = self.cleaned_data["template"]
        context = self.cleaned_data["context"]
        html_content = template_name.endswith(".html") and render_email_template_to_string(template_name, context) or ""
        text_content = template_name.endswith(".txt") and render_email_template_to_string(template_name, context) or ""
        kwargs = {
            "subject": subject,
            "recipients": [recipient],
            "html_content": html_content,
            "text_content": text_content,
        }
        db_msg = Message.make(**kwargs)
        db_msg.save()
