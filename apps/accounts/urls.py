# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("auth/", views.auth, name="auth"),
    path("test_login/", views.test_login, name="test_login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
