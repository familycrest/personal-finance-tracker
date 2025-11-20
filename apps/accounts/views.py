from django.contrib.auth import login as sys_login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)

from django.conf import settings as cfg

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
            if cfg.EMAIL_AUTHENTICATION:
                # Make the user [inside the form] inactive until they
                # authenticate. This means that they have practically no
                # permissions until then.
                #
                # TODO: Commenting this out for now due to a login bug.
                # If a user forgets to authenticate their account after signup,
                # they cannnot log in because their account is inactive, and
                # cannot signup again because an acocunt exists with the name.
                #
                # This is functionally still the same, but now the user is
                # active from the start. Actually, this still satisfies the
                # user story.
                # form.instance.is_active = False
                user = form.save()

                # Return the form to enter the emailed authentication code
                return utils.new_auth_form(request, user)
            else:
                # Save, login and redirect the user to the dashboard
                user = form.save()
                sys_login(request, user)
                return redirect("dashboard")

    return render(request, "accounts/signup.html", {"form": form})


def login(request):
    # For now, this just sends an auth code when you enter your email
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method != "POST":
        # Send the page for normal requests
        form = forms.EmailAuthenticationForm()
        return render(request, "accounts/login.html", {"form": form})

    # Process the form for submissions
    form = forms.EmailAuthenticationForm(request, request.POST)

    # Invalid forms will be sent back to the user, errors and all
    if not form.is_valid():
        manual_username = form.cleaned_data.get("username", None)

        if manual_username is not None:
            # There is a possibility that the user is still inactive.
            # Manually find a user to check and determine, in order to
            # return the correct error.
            try:
                manual_user = UserModel.objects.get(username=manual_username)

                # Replace all errors with a "not yet activated" errror if the
                # account exists but is not active
                if not manual_user.is_active:
                    form.errors.clear()
                    form.add_error(None, "This account has not yet been activated.")
            except UserModel.DoesNotExist:
                # If the user doesn't actually exist, just continue with the
                # usual error
                pass

        return render(request, "accounts/login.html", {"form": form})

    try:
        user = form.get_user()

        if cfg.EMAIL_AUTHENTICATION:
            # Send back a new auth form
            return utils.new_auth_form(request, user)
        else:
            # Just login and redirect the user
            sys_login(request, user)
            return redirect("dashboard")

    except AuthSessionExistsException:
        # This covers the creation of a code while one already exists
        form = forms.EmailAuthenticationForm()

        # TODO: Maybe tell the user when it will expire?
        return render(
            request,
            "accounts/auth.html",
            {
                "form": form,
                "error": "There is already an active code for your account. Please wait until it expires before generating a new one.",
            },
        )

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
        verified_user.save()
        sys_login(request, verified_user)

        response = redirect("dashboard")
        response.delete_cookie("target")

        return response

    except IndexError:
        # This covers "not found"-type errors
        # TODO: Either send to a 401 page or include a banner message on the homepage
        return redirect("home")

    except ValueError:
        # This covers "this is wrong"-type errors
        form = forms.EmailAuthenticationForm()

        return render(
            request,
            "accounts/auth.html",
            {
                "form": form,
                "error": "The code you supplied is incorrect. Please try again.",
            },
        )

    except AuthSessionExpiredException:
        # This covers if a session has expired
        form = forms.EmailAuthenticationForm()

        response = render(
            request,
            "accounts/auth.html",
            {
                "form": form,
                "error": "The authentication session has expired.",
                "regenerate": True,
            },
        )

        response.delete_cookie("target")

        return response


@login_required
def notification_mark_read(request, notif_id):
    if notif_id:
        try:
            notif = models.Notification.objects.get(
                pk=notif_id, user=request.user
            )  # add this for security so others can't delete your request
            notif.is_read = True
            notif.save()

            return HttpResponse(status=200)
        except models.Notification.DoesNotExist:
            return HttpResponseNotFound(f"notification {notif_id} does not exist")
    else:
        return HttpResponseBadRequest("must include notification ID in request")


@login_required
def notification_delete(request, notif_id):
    if notif_id:
        try:
            notif = models.Notification.objects.get(
                pk=notif_id, user=request.user
            )  # add this for security so others can't delete your request)
            notif.delete()

            return HttpResponse(status=200)
        except models.Notification.DoesNotExist:
            return HttpResponseNotFound(f"notification {notif_id} does not exist")
    else:
        return HttpResponseBadRequest("must include notification ID in request")
