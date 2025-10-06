from django.contrib.auth import login as auth_login, get_user_model, authenticate
from django.core.signing import Signer
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Model
    
from . import forms, models, utils

UserModel = get_user_model()

def signup(request):
    # Redirect the user to the dashboard if they're already logged in
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method != "POST":
        # Send the page for normal requests
        form = forms.CustomUserCreationForm()
    else:
        # Process the form for submissions
        form = forms.CustomUserCreationForm(request.POST)
        
        # Invalid forms will be sent back to the user, errors and all
        if form.is_valid():
            # Save the new user, but don't activate the account just yet
            user = form.save() 
            user.is_active = False

            return utils.new_auth_form(request, user)

    return render(request, "accounts/signup.html", {"form": form})

def login(request):
    # For now, this just sends an auth code when you enter your email
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method != "POST":
        # Send the page for normal requests
        form = forms.AuthenticationForm()
    else:
        # Process the form for submissions
        form = forms.AuthenticationForm(None, request.POST)
        
        # Invalid forms will be sent back to the user, errors and all
        if form.is_valid():
            user = form.get_user()
            
            return utils.new_auth_form(request, user)

    return render(request, "accounts/login.html", {"form": form})

def auth(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Ignore and redirect all requests which aren't form submissions
    if request.method != "POST":
        return redirect("home")
    
    try:
        # Extract user's email from the secure cookie
        target_email = utils.extract_target_email(request.COOKIES)
        
        # Verify user by the code they submitted
        form = forms.EmailVerificationForm(request.POST)
        verified_user = utils.verify_email_verification_form(target_email, form)
        
        # Login user
        verified_user.is_active = True
        auth_login(request, verified_user)
        
        response = redirect("dashboard")
        response.delete_cookie("target")
        
        return response

    except IndexError as e:
        # This covers "not found"-type errors
        return redirect("home")

    except ValueError as e:
        # This covers "this is wrong"-type errors
        form = forms.EmailVerificationForm()

        return render(request, "accounts/auth.html", {
            "email": target_email,
            "form": forms.EmailVerificationForm,
            "error": "The code you supplied is incorrect. Please try again."
        })

    except TimeoutError as e:
        # This covers expiry
        form = forms.EmailVerificationForm()

        return render(request, "accounts/auth.html", {
            "email": target_email,
            "form": forms.EmailVerificationForm,
            "error": "The authentication session has expired.",
            "regenerate": True
        })
