from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms import widgets


# Temporary fix for changing auth model from User to UserAccount
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        
class EmailVerificationForm(forms.Form):
    # a set-length text field with disabled autocomplete/suggestions
    # (do not remember previous codes)
    code = forms.CharField(
        label="Enter code (case insensitive)",
        max_length=6,
        widget=widgets.TextInput(attrs={"autocomplete": "off"})
    )

class TestLoginForm(forms.Form):
    email = forms.EmailField(label="Enter your email")