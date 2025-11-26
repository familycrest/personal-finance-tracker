# The tests in this file focus on email authentication rather than the basic signup/login/logout behavior.

from datetime import timedelta
from time import sleep

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.signing import Signer

from ..models import AuthSession

UserModel = get_user_model()
signer = Signer()

"""
This class implements convenience methods for making signup, login, and auth
requests. The other classes extend this and inherit its convenience methods.
"""


class BaseAccountsTestCase(TestCase):
    def send_signup_request(self, username, password):
        return self.client.post(
            reverse("signup"),
            {
                "username": username,
                "password1": password,
                "password2": password,
            },
        )

    def send_login_request(self, username, password):
        return self.client.post(
            reverse("login"), {"username": username, "password": password}
        )

    def send_auth_request(self, code):
        return self.client.post(reverse("auth"), {"code": code})


@override_settings(AUTH_SESSION_MAX_AGE=timedelta(seconds=2))
class SignUpAuthTests(BaseAccountsTestCase):
    """
    This test intentionally ends in a session timeout. It has multiple sections
    because these steps must happen in a sequence and with some persistent
    data.
    """

    def test_signup_into_timeout(self):
        """Attempt to use illegitimate cookie to access `auth`"""
        self.client.cookies["target"] = "invalidcode"
        response = self.send_auth_request("")

        # Did we get redirected?
        self.assertRedirects(response, reverse("home"))

        """ Attempt to use missing cookie to access `auth` """
        self.client.cookies["target"] = None
        response = self.send_auth_request("")

        # Did we get redirected?
        self.assertRedirects(response, reverse("home"))

        """ Send signup request and test that the auth form is returned """
        username = ("signup_auth_test_user_0",)
        password = r"9eb5F~#2jupEvfqM"
        response = self.send_signup_request(username, password)

        # Were we sent the authentication form?
        self.assertTemplateUsed(response, "accounts/auth.html")

        # Is the `target` cookie set?
        self.assertIsNotNone(self.client.cookies["target"])

        """ Test that the sent session token matches the auth session on the database """
        target_cookie = self.client.cookies["target"]

        # Decrypt session token
        signer = Signer()
        session_token = signer.unsign(target_cookie.value)

        # Manually find the new auth session
        database_session = AuthSession.objects.get(session_token=session_token)

        # Does the sent session token match what's in the database?
        self.assertEqual(database_session.session_token, session_token)

        """ Attempt to submit an auth form with invalid code """
        response = self.send_auth_request("foobar")

        # Are we still logged out?
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Are we still on the same page?
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/auth.html")

        # Did we get the appropriate error?
        self.assertContains(
            response, "The code you supplied is incorrect. Please try again."
        )

        """ Attempt to login before authentication """
        response = self.send_login_request(username, password)

        # Are we still logged out?
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Are we still on the same page?
        self.assertTemplateUsed(response, "accounts/auth.html")

        """ Attempt to submit auth form (even with correct code) after expiration """
        # Purposely wait until expiration
        sleep(2)

        response = self.send_auth_request(database_session.code)

        # Does it contain the correct error?
        self.assertContains(response, "The authentication session has expired.")

        # Did the target cookie get deleted?
        self.assertEqual(self.client.cookies["target"].value, "")

    """
    This test performs a successful signup and login.
    """

    def test_signup_successful(self):
        username = ("signup_auth_test_user_1",)
        password = r"a2E7x4nPZykHek$~"
        response = self.send_signup_request(username, password)

        """ Submit correct code """
        target_cookie = self.client.cookies["target"]
        session_token = signer.unsign(target_cookie.value)
        database_session = AuthSession.objects.get(session_token=session_token)
        response = self.send_auth_request(database_session.code)

        # Did we get redirected to the dashboard?
        self.assertRedirects(response, reverse("dashboard"))

        # Are we logged in?
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Did the target cookie get deleted?
        self.assertEqual(self.client.cookies["target"].value, "")


@override_settings(AUTH_SESSION_MAX_AGE=timedelta(seconds=2))
class LoginAuthTests(BaseAccountsTestCase):
    """
    This test performs a successful login.
    """

    def test_login(self):
        username = "login_auth_test_user_0"
        password = r"^CV&U9ynrF&$4hP$"
        response = self.send_signup_request(username, password)

        # Sign up successfully to set up a user to login with
        target_cookie = self.client.cookies["target"]
        session_token = signer.unsign(target_cookie.value)
        database_session = AuthSession.objects.get(session_token=session_token)
        response = self.send_auth_request(database_session.code)

        # Are we logged in?
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Log out
        response = self.client.post(reverse("logout"))

        # Are we logged out?
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        """ Create an auth session """
        response = self.send_login_request(username, password)

        # Store new session token
        target_cookie = self.client.cookies["target"]
        session_token = signer.unsign(target_cookie.value)
        database_session = AuthSession.objects.get(session_token=session_token)

        # Have we been sent the auth page?
        self.assertTemplateUsed(response, "accounts/auth.html")

        """ Attempt to create another code while one already exists """
        response = self.send_login_request(username, password)

        # Have we been sent the auth page?
        self.assertTemplateUsed(response, "accounts/auth.html")

        # Does it contain the correct error?
        self.assertContains(
            response,
            "There is already an active code for your account. Please wait until it expires before generating a new one.",
        )

        """ Submit correct code """
        response = self.send_auth_request(database_session.code)

        # Are we logged in?
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Did we get redirected to the dashboard?
        self.assertRedirects(response, reverse("dashboard"))

        # Did the target cookie get deleted?
        self.assertEqual(self.client.cookies["target"].value, "")
