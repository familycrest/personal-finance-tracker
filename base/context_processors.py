from django.http import HttpResponse, HttpRequest

def notifications(request: HttpRequest):
    """
    Add notifications to all rendered templates, so that it does not need to be
    manually processed added to every `render()` call.
    """
    
    print("context processor called")
    
    notifications = request.user.get_notifications()
    
    return {
        "notifications": notifications
    }
    
