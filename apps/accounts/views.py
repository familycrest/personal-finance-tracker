from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Model

from . import forms, models, authentication_service

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
                
                code = authentication_service.create_auth_code(current_user)
                
                print(f"generated code {code}")
                
                auth_codes = models.AuthCode.objects.all()
                
                print("active auth codes:")

                for entry in auth_codes:
                    print(f"  {entry.user.email}, {entry.code}")
                
                auth_form = forms.EmailVerificationForm()

                response = render(request, "accounts/auth.html", { "email": email, "form": auth_form })  # redirect to auth
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
    
    user = get_user_model()

    if request.method == "POST":
        try:
            # extract target email
            target_email = request.COOKIES.get("target_email", None)

            if target_email is None:
                raise IndexError("target_email cookie was not set")
                
            # get auth code associated with that email
            try:
                current_user = user.objects.get(email=target_email)
                auth_code = models.AuthCode.objects.get(user=current_user)
            except Model.DoesNotExist as e:
                # both statements are caught with one error to prevent email scanning attacks
                raise IndexError(f"no user or auth code found for target_email {target_email}")
                
            # extract auth code
            form = forms.EmailVerificationForm(request.POST)
            
            if not form.is_valid():
                raise ValueError(f"form is invalid!")
                
            test_auth_code = form.cleaned_data["code"].upper()
            print(f"user supplied code {test_auth_code}")
            
            # validate auth code
            if test_auth_code != auth_code.code:
                raise ValueError(f"code does not match!")
                
            print(f"CODE MATCHES!")
            
            auth_code.delete()
            
            print(f"auth code deleted")
            
            response = HttpResponse("yay!!!")
            response.delete_cookie("target_email")

            return response

        except IndexError as e:
            # this covers "not found"-type errors
            print(e)
            redirect("home")

        except ValueError as e:
            # this covers "this is wrong"-type errors
            print(e)
            form = forms.EmailVerificationForm()
            return render(request, "accounts/auth.html", {
                "email": target_email,
                "form": forms.EmailVerificationForm,
                "error": "The code you supplied was invalid. Please try again."
            })
    else:
        return redirect("home")
