"""
URL configuration for personal_finance_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# personal_finance_tracker/urls.py

from django.contrib import admin
from django.urls import path, include
from . import views as project_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Public homepage
    path("", project_views.home, name="home"),
    # Dashboard after login
    path("dashboard", project_views.dashboard, name="dashboard"),
    # Accounts
    path("accounts/", include("apps.accounts.urls")),
    # Finances
    path("finances/", include("apps.finances.urls"), name="finances"),
    path("notifs", project_views.add_notif_dummy, name="notifs")
]

# Sets the view for handling 404 errors/pages that don't exist
handler404 = "base.views.custom_404"
