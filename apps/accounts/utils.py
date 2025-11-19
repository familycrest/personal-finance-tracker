from datetime import datetime, timedelta, timezone
from secrets import token_hex

from django.contrib.auth import get_user_model
from django.core.signing import Signer, BadSignature
from django.http import HttpRequest
from django.shortcuts import render, redirect

from django.conf import settings as cfg

from . import forms
from .models import AuthSession, AuthSessionExpiredException

UserModel = get_user_model()


def extract_session_token(cookies: list) -> str:
    # Extract session token
    target_cookie = cookies.get("target", None)

    if target_cookie is None:
        raise IndexError("`target` cookie was not set.")

    try:
        # Unsign it to confirm that the request is legitimate
        signer = Signer()
        session_token = signer.unsign(target_cookie)
    except BadSignature:
        raise IndexError("`target` cookie is invalid")

    return session_token


def verify_email_auth_form(
    session_token: str, form: forms.EmailAuthenticationForm
) -> UserModel:
    # Find auth code associated with that email
    try:
        session = AuthSession.objects.get(session_token=session_token)
        current_user = session.user

    except (UserModel.DoesNotExist, AuthSession.DoesNotExist):
        # Both errors are made into one to prevent email scanning attacks
        raise IndexError("No user or auth code found.")

    # Check if expired
    if session.is_expired():
        raise AuthSessionExpiredException()

    # Extract auth code
    if not form.is_valid():
        raise ValueError("Form is invalid.")

    supplied_code = form.cleaned_data["code"].upper()

    # Validate auth code
    if not session.verify_against_code(supplied_code):
        raise ValueError("Code does not match!")

    # Clean up
    session.delete()

    return current_user


def new_auth_form(request, user):
    # Create an auth code object and send it to the user
    session = AuthSession.create_from_user_account(user)
    session.send_verif_email()

    # Sign the token in order to prevent tampering with the cookie
    signer = Signer()
    signed_token = signer.sign(session.session_token)

    # Send a form with the cookie
    form = forms.EmailAuthenticationForm()

    response = render(
        request,
        "accounts/auth.html",
        {
            "email": user.email,
            "form": form,
            "session_validity": cfg.AUTH_SESSION_MAX_AGE_STRING,
        },
    )

    response.set_cookie("target", signed_token)

    return response
