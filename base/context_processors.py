from django.http import HttpResponse, HttpRequest

def notifications(request: HttpRequest):
    """
    Add notifications to all rendered templates, so that it does not need to be
    manually processed added to every `render()` call.
    """
    
    if request.user.is_authenticated:
        notifications = request.user.get_notifications().order_by("creation_date")

        return {
            "notifications": {
                "unread": list(filter(lambda n: not n.is_read, notifications)),
                "read": list(filter(lambda n: n.is_read, notifications)),
            }
        }
    else:
        return { }