# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("auth/", views.auth, name="auth"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("notifications/<int:notif_id>/mark_read", views.notification_mark_read, name="notif_mark_read")
]
