import base64
import binascii
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import jwt
from django.conf import settings

from .models import User


class TokenGenerator(ABC):
    @abstractmethod
    def make_token(self, user: User) -> str:
        pass

    @abstractmethod
    def check_token(self, token: str) -> bool:
        pass


class JSONWebTokenGenerator(TokenGenerator):
    JWT_SECRET_KEY = settings.SECRET_KEY

    user_kwargs = ["email"]
    token_expiration = 60 * 60 * 24  # 1 day

    @classmethod
    def make_token(cls, user: User, expiry: Optional[int] = None) -> str:
        if expiry is None:
            # Must be UTC time!
            expiry = datetime.now(tz=timezone.utc).timestamp() + cls.token_expiration

        payload = {"exp": expiry, **{k: getattr(user, k) for k in cls.user_kwargs}}
        jwt_token = jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm="HS256")
        return base64.urlsafe_b64encode(jwt_token.encode("utf-8")).decode("utf-8")

    @classmethod
    def check_token(cls, token: str) -> User | None:
        try:
            jwt_token = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            payload = jwt.decode(jwt_token, cls.JWT_SECRET_KEY, algorithms=["HS256"])

            return User.objects.get(**{k: payload[k] for k in cls.user_kwargs})
        except (KeyError, User.DoesNotExist, jwt.ExpiredSignatureError, binascii.Error):
            return None


class EmailVerificationTokenGenerator(JSONWebTokenGenerator):
    JWT_SECRET_KEY = settings.SECRET_KEY

    token_expiration = 60 * 60 * 24 * 3  # 3 days


class PasswordResetTokenGenerator(JSONWebTokenGenerator):
    JWT_SECRET_KEY = settings.SECRET_KEY

    token_expiration = 60 * 60 * 6  # 6 hours
