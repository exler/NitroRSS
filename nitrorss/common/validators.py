from typing import Optional, Sequence

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

from nitrorss.common._disposable_email_domains import DISPOSABLE_EMAIL_DOMAINS


@deconstructible
class DomainBlacklistValidator:
    blacklist = []

    domain_regex = r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)"

    message = _("This domain is blacklisted. Please contact the site administrator.")
    code = "domain_blacklisted"

    def __init__(
        self, blacklist: Optional[Sequence[str]] = None, message: Optional[str] = None, code: Optional[str] = None
    ) -> None:
        if blacklist is not None:
            self.blacklist = blacklist
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

        self.regex = _lazy_re_compile(self.domain_regex)

    def __call__(self, value: str) -> None:
        match = self.regex.match(value)
        if match and match[1] in self.blacklist:
            raise ValidationError(self.message, code=self.code)


@deconstructible
class DisposableEmailBlacklistValidator(DomainBlacklistValidator):
    blacklist = DISPOSABLE_EMAIL_DOMAINS
