from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.finances.models import (
    Analytics
)


def home(request):
    return render(request, "home.html")


@login_required
def dashboard(request):
    user = request.user
    analytics = Analytics.objects.filter(user_account=user).first()
    if analytics:
        Analytics.objects.all().delete()
    
    analytics = Analytics.objects.create(user_account=user)
    analytics.generate_account_report()
    
    reports = analytics.reports.all()
    return render(request, "dashboard.html", { "reports": reports, "user": user })

# View for invalid requests
def custom_404(request, exception):
    return render(request, "404.html", status=404)

