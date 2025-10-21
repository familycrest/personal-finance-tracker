from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django import forms
from django.forms import widgets
from django.views.decorators.debug import sensitive_variables

UserModel = get_user_model()


# Temporary fix for changing auth model from User to UserAccount
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        
class EmailAuthenticationForm(forms.Form):
    # a set-length text field with disabled autocomplete/suggestions
    # (do not remember previous codes)
    code = forms.CharField(
        label="Enter code (case insensitive)",
        max_length=6,
        widget=widgets.TextInput(attrs={"autocomplete": "off"})
    )

class CustomLoginForm(forms.Form):
    """
    This is very similar to the stock form but using only email/password
    instead of username/password.

    TODO: Ideally, this should be a login form that accepts an email *or* a
    username, just like how so many other sites do it. Doing it username-only
    is fine too, but whichever way we go, we will need to require emails for
    all users. This will have to be implemented in future PRs. For now, the
    stock `AuthenticationForm` is used.
    """

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            "autofocus": "true",
            "maxlength": 254
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"})
    )

    error_messages = {
        "invalid_login": "Invalid email or password.",
        "inactive": "This account must be verified first."
    }
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        
        self.fields["email"].max_length = 254
        self.fields["email"].widget.attrs["maxlength"] = 254

    @sensitive_variables()
    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if email is not None and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid-login",
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
                
        return self.cleaned_data
                
    def get_user(self):
        return self.user_cache
