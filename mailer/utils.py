import base64
import pickle  # nosec B403

from django.core.mail import EmailMessage


class EmailDatabaseSerializer:
    @staticmethod
    def email_to_db(email: EmailMessage) -> str:
        return base64.encodebytes(pickle.dumps(email)).decode("ascii")

    @staticmethod
    def db_to_email(data: str) -> EmailMessage | None:
        return pickle.loads(base64.decodebytes(data.encode("ascii")))  # nosec B301
