from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Temporary fix for changing auth model from User to UserAccount
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
