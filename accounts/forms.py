# accounts/forms.py
# this was created because we created a custom user model.
# Django uses default settings for auth.user.
# You need to make a form to create a custom user for Django
# to recognize.

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # may add "email" later