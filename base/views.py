from urllib.parse import urlparse

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
    
from django.http import HttpRequest
from apps.finances.models import (
    Analytics
)


def home(request):
    return render(request, "home.html")


@login_required
def dashboard(request: HttpRequest):
    banner_message = None

    """
    # gonna finish this later; it should be using url params instead of header. it's an optional, low prio feature
    if :
        parsed_referer = urlparse(referer)
        referer_path = parsed_referer.path
        
        print(referer_path)
        
        match referer_path:
            case "/accounts/auth":
                banner_message = "You have successfully been authenticated and signed in!"
            case "/accounts/signup" | "/accounts/login":
                banner_message = "You are already logged into an account."
    """

    user = request.user
    analytics = Analytics.objects.filter(user_account=user).first()
    if analytics:
        Analytics.objects.all().delete()
    
    analytics = Analytics.objects.create(user_account=user)
    analytics.generate_account_report()
    
    reports = analytics.reports.all()

    return render(request, "dashboard.html", {"login_message": banner_message, "reports": reports, "user": user})


# View for invalid requests
def custom_404(request, exception):
    return render(request, "404.html", status=404)

