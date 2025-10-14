from botocore.exceptions import ClientError, WaiterError
from ses_identities import SesIdentity
from ses_templates import SesTemplate
from ses_generate_smtp_credentials import calculate_key
import boto3


class SesMailSender:
    def __init__(self, ses_client):
        self.ses_client = ses_client

    def send_email(self, source, destination, subject, text, html, reply_tos=None):
        send_args = {
            "Source": source,
            "Destination": destination.to_service_format(),
            "Message": {
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": text},
                    "Html": {"Data": html}
                }
            }
        }

        if reply_tos is not None:
            send_args["ReplyToAddrsses"] = reply_tos
        
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response["MessageId"]

        except ClientError:
            print("aw man")
        
        return message.id

ses_client = boto3.resource("s3")
sender = SesMailSender(ses_client)
sender.send_email("jake@skybldev.eu.org")

