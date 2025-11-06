from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
    
from django.http import HttpRequest


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

    return render(request, "dashboard.html", {"login_message": banner_message})


# View for invalid requests
def custom_404(request, exception):
    return render(request, "404.html", status=404)

@login_required
def add_notif_dummy(request):
    if request.method == "POST":
        title = request.POST.get("title") or "a title" 
        message = request.POST.get("message") or "a message"
        
        request.user.add_notification(title, message)
        
        return redirect("dashboard")
