from datetime import datetime, timedelta, timezone
from secrets import token_hex

from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.http import HttpRequest
from django.shortcuts import render, redirect

from base.settings import AUTH_SESSION_MAX_AGE, AUTH_SESSION_MAX_AGE_STRING

from . import models, forms
    
UserModel = get_user_model()

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
    try:
        current_user = UserModel.objects.get(email=target_email)
        auth_code_obj = models.AuthCode.objects.get(user=current_user)

    except (UserModel.DoesNotExist, models.AuthCode.DoesNotExist):
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
    
    # Clean up
    auth_code_obj.delete()
        
    return current_user

def new_auth_form(request, user):
    # Create an auth code object and send it to the user
    auth_code_obj = models.AuthCode.create_from_user_account(user)
    auth_code_obj.send_verif_email()

    print("signing email")
    
    # Sign the email in order to prevent tampering with the cookie
    signer = Signer()
    signed_email = signer.sign(user.email)

    print("sending stuff back")

    # Send a form with the cookie
    form = forms.EmailVerificationForm()
    
    response = render(request, "accounts/auth.html", {
        "email": user.email,
        "form": form,
        "session_validity": AUTH_SESSION_MAX_AGE_STRING
    })

    response.set_cookie("target", signed_email)

    return response