from datetime import datetime, timedelta, timezone
from secrets import token_hex

from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.http import HttpRequest

from base.settings import AUTH_SESSION_MAX_AGE

from . import models, forms

def extract_target_email(cookies: list) -> str:
    # Extract target cookie
    target_cookie = cookies.get("target", None)

    if target_cookie is None:
        raise IndexError("`target` cookie was not set.")
        
    # Unsign it to confirm that the request is legitimate
    signer = Signer()
    target_email = signer.unsign(target_cookie)
    
    return target_email

def verify_email_verification_form(
    target_email: str,
    form: forms.EmailVerificationForm
) -> models.UserAccount:
    # Find auth code associated with that email
    user = get_user_model()

    try:
        current_user = user.objects.get(email=target_email)
        auth_code_obj = models.AuthCode.objects.get(user=current_user)

    except (user.DoesNotExist, models.AuthCode.DoesNotExist):
        # Both errors are made into one to prevent email scanning attacks
        raise IndexError(f"No user or auth code found for email {target_email}.")
    
    # Check if expired
    time_since_issued = datetime.now(timezone.utc) - auth_code_obj.issued
    print(time_since_issued)
    if time_since_issued > AUTH_SESSION_MAX_AGE:
        raise TimeoutError(f"Auth session has expired.")

    # Extract auth code
    if not form.is_valid():
        raise ValueError(f"Form is invalid.")
        
    supplied_auth_code = form.cleaned_data["code"].upper()
    
    # Validate auth code
    if supplied_auth_code != auth_code_obj.code:
        raise ValueError(f"Code does not match!")
        
    return current_user