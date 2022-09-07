from nitrorss.common.tokens import JSONWebTokenGenerator
from subscriptions.models import Subscription


class ConfirmSubscriptionTokenGenerator(JSONWebTokenGenerator):
    model = Subscription
    obj_kwargs = ["target_email", "feed_id"]
    token_expiration = 60 * 60 * 8  # 8 hours
