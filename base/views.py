from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
    
from django.http import HttpRequest


def home(request):
    return render(request, "home.html")

# View for invalid requests
def custom_404(request, exception):
    return render(request, "404.html", status=404)

@login_required
def add_notif_dummy(request):
    if request.method == "POST":
        title = request.POST.get("title") or "a title" 
        message = request.POST.get("message") or "a message"
        
        request.user.add_notification("test", title, message)
        
        return redirect("dashboard")
