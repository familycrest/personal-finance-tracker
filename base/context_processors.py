import json

from django.http import HttpResponse, HttpRequest
from django.forms.models import model_to_dict

def notifications(request: HttpRequest):
    """
    Add notifications to all rendered templates, so that it does not need to be
    manually processed added to every `render()` call.
    """
    
    if request.user.is_authenticated:
        notifications = list(request.user.get_notifications().order_by("-creation_date"))
        
        unread = []
        read = []
        
        for raw_notif in notifications:
            """Process a notification before it is sent to the template renderer."""
            notif = model_to_dict(raw_notif)
            msg = notif["message"]

            notif["creation_date"] = raw_notif.creation_date

            if notif["is_read"]:
                read.append(notif)
            else:
                unread.append(notif)

        return {
            "notifs": {
                "unread": unread,
                "read": read
            }
        }
    else:
        return { }