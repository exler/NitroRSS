import base64
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


class EmailVerificationTokenGenerator(TokenGenerator):
    JWT_SECRET_KEY = settings.SECRET_KEY
    DEFAULT_TOKEN_EXPIRATION = 259_200  # 3 days

    @classmethod
    def make_token(cls, user: User, expiry: Optional[int] = None) -> str:
        if expiry is None:
            # Must be UTC time!
            expiry = datetime.now(tz=timezone.utc).timestamp() + cls.DEFAULT_TOKEN_EXPIRATION

        payload = {"email": user.email, "exp": expiry}
        jwt_token = jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm="HS256")
        return base64.urlsafe_b64encode(jwt_token.encode("utf-8")).decode("utf-8")

    @classmethod
    def check_token(cls, token: str) -> User | None:
        try:
            jwt_token = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            payload = jwt.decode(jwt_token, cls.JWT_SECRET_KEY, algorithms=["HS256"])
            email = payload["email"]

            return User.objects.get(email=email)
        except (KeyError, User.DoesNotExist, jwt.ExpiredSignatureError):
            return None
