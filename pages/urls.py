from django.urls import path

from .views import HomePageView, SignupPageView, LoginPageView


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("signup/", SignupPageView.as_view(), name="signup"),
    path("login/", LoginPageView.as_view(), name="login"),
]
