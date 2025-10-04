from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


# Temporary fix for changing auth model from User to UserAccount
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        
class EmailVerificationForm(forms.Form):
    code = forms.CharField(label="Enter code", max_length=6)

class TestLoginForm(forms.Form):
    email = forms.EmailField(label="Enter your email")