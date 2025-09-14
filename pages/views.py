from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SignupPageView(TemplateView):
    template_name = "signup.html"


class LoginPageView(TemplateView):
    template_name = "login.html"
