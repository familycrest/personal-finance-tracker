from secrets import token_hex

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from . import models, forms

def verify_email_verification_form(request: HttpRequest) -> models.UserAccount:
    # Extract target email cookie
    target_email = request.COOKIES.get("target_email", None)

    if target_email is None:
        raise IndexError("`target_email` cookie was not set.")
        
    user = get_user_model()
    
    # Find auth code associated with that email
    try:
        current_user = user.objects.get(email=target_email)
        auth_code_obj = models.AuthCode.objects.get(user=current_user)

    except:
        # both statements are caught with one error to prevent email scanning attacks
        raise IndexError(f"No user or auth code found for email {target_email}.")
        
    # Extract auth code
    form = forms.EmailVerificationForm(request.POST)

    if not form.is_valid():
        raise ValueError(f"Form is invalid.")
        
    supplied_auth_code = form.cleaned_data["code"].upper()
    
    # Validate auth code
    if supplied_auth_code != auth_code_obj.code:
        raise ValueError(f"Code does not match!")

    return current_user

        

        

    
    
    

