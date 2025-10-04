from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Model

from . import forms, models, utils

def signup(request):
    # Redirect the user to the dashboard if they're already logged in
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    user = get_user_model()
    if request.method == "POST":
        form = forms.CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()  # save the new user
            user.is_active = False
            return redirect("dashboard")  # redirect to auth
        # TODO: Tell the user exactly why it was invalid

    else:
        form = forms.CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})

def test_login(request):
    # for now, this just sends an auth code when you enter your email
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    user = get_user_model()

    if request.method == "POST":
        form = forms.TestLoginForm(request.POST)
        
        if form.is_valid():
            print("form submitted!")
            
            email = form.cleaned_data["email"]
            
            print(f"form email is {email}")
            
            try:
                current_user = user.objects.get(email=email)

                print(f"found user for this email, username {current_user.username}")
                
                auth_code_obj = models.AuthCode.create_from_user_account(current_user)
                auth_code_obj.send_verif_email()
                
                auth_codes = models.AuthCode.objects.all()
                
                print("active auth codes:")

                for entry in auth_codes:
                    print(f"  {entry.user.email}, {entry.code}")

                auth_form = forms.EmailVerificationForm()

                response = render(request, "accounts/auth.html", { "email": email, "form": auth_form })
                # TODO: this should be hashed with the secret key
                response.set_cookie("target_email", current_user.email)
                return response
            except user.DoesNotExist as e:
                print(f"no user found :(")

        # TODO: Tell the user exactly why it was invalid

    else:
        form = forms.TestLoginForm()

    return render(request, "accounts/test_login.html", {"form": form})

def auth(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Ignore and redirect all requests which aren't form submissions
    if request.method != "POST":
        return redirect("home")
    
    try:
        verified_user = utils.verify_email_verification_form(request)
        
        print("User verified!")
        
        response = HttpResponse("You're verified")
        response.delete_cookie("target_email")
        
        return response

    except IndexError as e:
        # This covers "not found"-type errors
        print(f"IndexError when verifying user form: {e}") 
        print("Redirecting to home.")

        return redirect("home")

    except ValueError as e:
        # This covers "this is wrong"-type errors
        print(f"ValueError when verifying user form: {e}")
        print("Resending form.")

        form = forms.EmailVerificationForm()

        return render(request, "accounts/auth.html", {
            "email": target_email,
            "form": forms.EmailVerificationForm,
            "error": "The code you supplied was invalid. Please try again."
        })