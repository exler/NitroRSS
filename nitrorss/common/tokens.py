import base64
import binascii
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class TokenGenerator(ABC):
    @abstractmethod
    def make_token(self, obj: Any) -> str:
        pass

    @abstractmethod
    def check_token(self, token: str) -> Any | None:
        pass


class JSONWebTokenGenerator(TokenGenerator):
    JWT_SECRET_KEY = settings.SECRET_KEY

    model = None
    obj_kwargs = []
    token_expiration = 60 * 60 * 24  # 1 day

    @classmethod
    def make_token(cls, obj: Any, expiry: Optional[int] = None) -> str:
        if expiry is None:
            # Must be UTC time!
            expiry = datetime.now(tz=timezone.utc).timestamp() + cls.token_expiration

        payload = {"exp": expiry, **{k: getattr(obj, k) for k in cls.obj_kwargs}}
        jwt_token = jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm="HS256")
        return base64.urlsafe_b64encode(jwt_token.encode("utf-8")).decode("utf-8")

    @classmethod
    def check_token(cls, token: str) -> Any | None:
        try:
            jwt_token = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            payload = jwt.decode(jwt_token, cls.JWT_SECRET_KEY, algorithms=["HS256"])

            return cls.model.objects.get(**{k: payload[k] for k in cls.obj_kwargs})
        except (KeyError, ObjectDoesNotExist, jwt.ExpiredSignatureError, binascii.Error):
            return None
