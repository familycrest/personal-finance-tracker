"""
URL configuration for PersonalFinanceTrackerProject project.

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
# personal_finance_tracker_app/urls.py
from django.urls import path
from . import views as personal_finance_tracker_app_views  # this is to import app views

urlpatterns = [
    # this is the url for the homepage
    path("", personal_finance_tracker_app_views.home, name="home"),

    # Dashboard after login
    path("dashboard/", personal_finance_tracker_app_views.dashboard, name="dashboard"),

]
