# The tests in this file turn off email authentication, focusing on the webpage and form behavior.

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.tests import TestHelper
from itertools import product

UserModel = get_user_model()


@override_settings(EMAIL_AUTHENTICATION=False)
class SignUpPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Fetch default test user
        cls.user, cls.username = TestHelper.return_test_user()

    def test_signup_page_available_at_correct_url(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_page_available_by_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_is_correct(self):
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_correct_content_shown_when_user_is_not_authenticated(self):
        response = self.client.get(reverse("signup"))

        # Test the signup header
        self.assertContains(response, "<h2>Sign Up</h2>")

    def test_user_signup_with_existing_username(self):
        usernames = [
            self.username,  # Test existing username
            self.username.upper(),  # Test existing username but uppercase
        ]

        good_password = "55R@andOM!P@$$word89@#"

        for username in usernames:
            initial_user_count = UserModel.objects.count()

            response = self.client.post(
                reverse("signup"),
                {
                    "username": username,
                    "password1": good_password,
                    "password2": good_password,
                },
            )

            # Did the number of user accounts stay the same?
            self.assertEqual(UserModel.objects.count(), initial_user_count)

            # Was the user prevented from logging in?
            self.assertFalse(response.wsgi_request.user.is_authenticated)

            # Were we sent the appropriate error page and error?
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/signup.html")
            self.assertContains(
                response, "A user with that username already exists."
            )

    def test_user_signup_with_missing_fields(self):
        usernames = ["Randomuser27", ""]
        password1s = ["89%AJValidP@assword910", ""]
        password2s = ["89%AJValidP@assword910", ""]

        # Creates every combination of fields being present or not
        fields_combinations = product(usernames, password1s, password2s)

        # Test every combination of missing fields
        for username, password1, password2 in fields_combinations:
            # Skip when all fields are present because that would be testing a valid condition
            if username and password1 and password2:
                continue

            initial_user_count = UserModel.objects.count()
            response = self.client.post(
                reverse("signup"),
                {
                    "username": username,
                    "password1": password1,
                    "password2": password2,
                },
            )

            # Did the number of user accounts stay the same?
            self.assertEqual(UserModel.objects.count(), initial_user_count)

            # Was the user prevented from logging in?
            self.assertFalse(response.wsgi_request.user.is_authenticated)

            # Were we sent the appropriate error page and error?
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/signup.html")

            # Test for the correct error messages / elements, depending on which fields are missing.
            if not username:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_username_error"><li>This field is required.</li></ul>',
                )
            if not password1:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_password1_error"><li>This field is required.</li></ul>',
                )
            if not password2:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_password2_error"><li>This field is required.</li></ul>',
                )

    def test_user_signup_with_mismatched_passwords(self):
        initial_user_count = UserModel.objects.count()
        response = self.client.post(
            reverse("signup"),
            {
                "username": "AnotherRandomUser890",
                "password1": "ARandom$$$Possword",
                "password2": "ARandom$Password",
            },
        )

        # Did the number of user accounts stay the same?
        self.assertEqual(UserModel.objects.count(), initial_user_count)

        # Was the user prevented from logging in?
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Were we sent the correc error page?
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

        # Does it contain the appropriate error?
        self.assertContains(
            response,
            "The two password fields didn’t match.",
        )

    def test_successful_user_signup(self):
        new_username = "AProgrammerMan"
        password = r'2}h~*%uLUl"G~[x.bIi~'

        initial_user_count = UserModel.objects.count()
        response = self.client.post(
            reverse("signup"),
            {
                "username": new_username,
                "password1": password,
                "password2": password,
            },
        )

        # Did the user count increase by exactly one?
        self.assertEqual(initial_user_count + 1, UserModel.objects.count())

        # Was the account saved successfully?
        self.assertTrue(
            UserModel.objects.filter(username=new_username).exists()
        )

        # Were we logged in and redirected to the dashboard?
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse("dashboard"))

    def test_user_is_redirected_when_already_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("dashboard"))


@override_settings(EMAIL_AUTHENTICATION=False)
class LoginPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.username = TestHelper.return_test_user()

    def test_login_page_available_at_correct_url(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_available_by_name(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_is_correct(self):
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_correct_content_shown_when_user_is_not_authenticated(self):
        response = self.client.get(reverse("login"))

        # Does the header indicate that we aren't logged in?
        TestHelper.assert_unauthenticated_header(self, response)

        # Test for other page content
        self.assertContains(response, "<h2>Log In</h2>")

    def test_user_login_with_incorrect_or_no_data(self):
        usernames = ["incorrectUsername", ""]
        passwords = ["incorrectPassword$1", ""]

        # Create every combination possible for incorrect or no data. Such as incorrect username or no username.
        fields_combinations = product(usernames, passwords)
        # Test each field combination.
        for username, password in fields_combinations:
            response = self.client.post(
                reverse("login"), {"username": username, "password": password}
            )
            # For every case test user doesn't get logged in...
            # Are we still logged out?
            self.assertFalse(response.wsgi_request.user.is_authenticated)

            # Did we get the correct page instead of being redirected?
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/login.html")

            # Did we get the appropriate errors?
            if username and password:
                self.assertContains(
                    response,
                    "Please enter a correct username and password. Note that both fields may be case-sensitive.",
                )
            if not username:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_username_error"><li>This field is required.</li></ul>',
                )
            if not password:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_password_error"><li>This field is required.</li></ul>',
                )

    def test_user_login_with_correct_username_and_incorrect_or_no_password(
        self,
    ):
        username = "AProgrammerMan"
        real_pass = "@l`{N+l2_RCd$9Uz<|sM"
        incorrect_passwords = ["hitheremyguy", ""]

        UserModel.objects.create_user(username=username, password=real_pass)

        for password in incorrect_passwords:
            response = self.client.post(
                reverse("login"), {"username": username, "password": password}
            )

            # Are we still logged out?
            self.assertFalse(response.wsgi_request.user.is_authenticated)

            # Did we get the correct page instead of being redirected?
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/login.html")

            # Did we get the appropriate errors?
            if username and password:
                self.assertContains(
                    response,
                    "Please enter a correct username and password. Note that both fields may be case-sensitive.",
                )
            else:
                self.assertContains(
                    response,
                    '<ul class="errorlist" id="id_password_error"><li>This field is required.</li></ul>',
                )

    def test_user_login_with_correct_credentials(self):
        username = "TheComputerItself"
        password = "c3&CT:Rm<_;BAWu)JvAy"

        UserModel.objects.create_user(username=username, password=password)

        initial_user_count = UserModel.objects.count()

        response = self.client.post(
            reverse("login"), {"username": username, "password": password}
        )

        # Are we logged in?
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Did the number of users stay the same?
        self.assertEqual(initial_user_count, UserModel.objects.count())

        # Were we redirected to the dashboard?
        self.assertRedirects(response, reverse("dashboard"))

    def test_user_is_redirected_when_already_logged_in(self):
        self.client.force_login(LoginPageTests.user)
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("dashboard"))


class LogoutViewTests(TestCase):
    def test_logout_view_available_at_correct_url(self):
        response = self.client.post("/accounts/logout/")
        self.assertRedirects(response, reverse("home"))

    def test_logout_view_available_by_name(self):
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))

    def test_user_gets_logged_out(self):
        user, username = TestHelper.return_test_user()
        self.client.force_login(user)

        response = self.client.post(reverse("logout"))

        # Are we logged out?
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Were we redirected to the homepage?
        self.assertRedirects(response, reverse("home"))
