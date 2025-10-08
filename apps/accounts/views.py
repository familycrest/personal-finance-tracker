from django.contrib.auth import login as sys_login, get_user_model, authenticate
from django.core.signing import Signer
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Model
    
from . import forms, models, utils
from .models import AuthSessionExpiredException, AuthSessionExistsException

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
        return render(request, "accounts/login.html", {"form": form})

    # Process the form for submissions
    form = forms.AuthenticationForm(None, request.POST)
    
    # Invalid forms will be sent back to the user, errors and all
    if not form.is_valid():
        return render(request, "accounts/login.html", {"form": form})
    
    try:
        # Obtain the user and try to send back a new auth form
        user = form.get_user()
        return utils.new_auth_form(request, user)

    except AuthSessionExistsException:
        # This covers the creation of a code while one already exists
        form = forms.EmailAuthenticationForm()

        # TODO: Maybe tell the user when it will expire?
        return render(request, "accounts/auth.html", {
            "form": forms.EmailAuthenticationForm,
            "error": "There is already an active code for your account. Please wait until it expires before generating a new one.",
        })


    return render(request, "accounts/login.html", {"form": form})

def auth(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Ignore and redirect all requests which aren't form submissions
    if request.method != "POST":
        return redirect("home")
    
    try:
        # Extract unique session token from the secure cookie
        session_token = utils.extract_session_token(request.COOKIES)
        
        # Verify user by the code they submitted
        form = forms.EmailAuthenticationForm(request.POST)
        verified_user = utils.verify_email_auth_form(session_token, form)
        
        # Login user
        verified_user.is_active = True
        sys_login(request, verified_user)
        
        response = redirect("dashboard")
        response.delete_cookie("target")
        
        return response

    except IndexError as e:
        # This covers "not found"-type errors
        # TODO: Either send to a 401 page or include a banner message on the homepage
        return redirect("home")

    except ValueError as e:
        # This covers "this is wrong"-type errors
        form = forms.EmailAuthenticationForm()

        return render(request, "accounts/auth.html", {
            "form": forms.EmailAuthenticationForm,
            "error": "The code you supplied is incorrect. Please try again."
        })

    except AuthSessionExpiredException:
        # This covers if a session has expired
        form = forms.EmailAuthenticationForm()

        response = render(request, "accounts/auth.html", {
            "form": forms.EmailAuthenticationForm,
            "error": "The authentication session has expired.",
            "regenerate": True
        })

        response.delete_cookie("target")
        
        return response
