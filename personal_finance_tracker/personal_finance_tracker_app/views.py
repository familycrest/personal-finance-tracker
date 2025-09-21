# personal_finance_tracker_app/views.py
# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "personal_finance_tracker_app/home.html")


@login_required
def dashboard(request):
    return render(request, "personal_finance_tracker_app/dashboard.html")
