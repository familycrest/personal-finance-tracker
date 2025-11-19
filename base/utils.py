from botocore.exceptions import ClientError, WaiterError
import boto3

from django.contrib.auth import get_user_model
from django.template.loader import get_template

from django.conf import settings as cfg


# This implements a Singleton class, meaning that whenever and whereever this
# class is called, there will only be one (shared) instance of it.
class EmailBackend:
    # By default, this class has no instances.
    _instance = None

    # Override the __new__ method to take control of what happens *before*
    # __init__ is called. This allows us to only create and thus return a
    # single instance of the class.
    def __new__(cls):
        # This is only called once, the first time the class is initialized.
        if not hasattr(cls, "instance"):
            cls.instance = super(EmailBackend, cls).__new__(cls)
            # Because we can't use __init__ anymore, the constructor can be
            # extended using a setup() function.
            cls.setup(cls)

        return cls.instance

    # Override this to implement instantiation behavior
    @classmethod
    def setup(cls):
        pass

    # Override this to implement sending behavior
    def send_email(self, source, destination, subject, text, html):
        pass


class DummyEmailBackend(EmailBackend):
    def setup(cls):
        print("DummyEmailBackend :: Backend created")

    def msg(self, msg):
        print(f"DummyEmailBackend :: {msg}")

    def send_email(self, source, destination, subject, text, html):
        self.msg(f"Sending email as `{source}` to `{destination}`")
        self.msg(f"  subject: {subject}")
        self.msg(f"  plaintext: {text}")
        self.msg(f"  html: {html}")


class SesEmailBackend(EmailBackend):
    def setup(cls):
        cls.ses_client = boto3.client("ses")
        print("SesEmailBackend :: Backend created")

    def send_email(self, source, destination, subject, text, html):
        send_args = {
            "Source": source,
            "Destination": {"ToAddresses": [destination]},
            "Message": {
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
            },
        }

        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response["MessageId"]

        except Exception as e:
            raise Exception(
                "SesEmailBackend :: There was an error sending this email: {e}"
            )

        print(
            f"SesEmailBackend :: Sending email as `{source}` to `{destination}`"
        )

        return message_id
