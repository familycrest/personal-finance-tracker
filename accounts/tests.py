from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from personal_finance_tracker.tests import TestHelper
from itertools import product


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

        # Test that the correct navigation links are present
        TestHelper.assert_unauthenticated_nav(self, response)

        # Test the form content
        self.assertContains(response, '<label for="id_username">Username:</label>')
        self.assertContains(response, '<input type="text" name="username" maxlength="150" autocapitalize="none" autocomplete="username" autofocus required aria-describedby="id_username_helptext" id="id_username">')
        self.assertContains(response, '<label for="id_password1">Password:</label>')
        self.assertContains(response, '<input type="password" name="password1" autocomplete="new-password" required aria-describedby="id_password1_helptext" id="id_password1">')
        self.assertContains(response, '<label for="id_password2">Password confirmation:</label>')
        self.assertContains(response, '<input type="password" name="password2" autocomplete="new-password" required aria-describedby="id_password2_helptext" id="id_password2">')
        self.assertContains(response, '<button type="submit">Sign Up</button>')

        # Test the signup header
        self.assertContains(response, '<h2>Sign Up</h2>')
    
    def test_user_signup_with_invalid_username(self):
        usernames = [
            SignUpPageTests.username, # Test existing username
            SignUpPageTests.username.upper() # Test existing username but uppercase
        ]

        good_password = "55R@andOM!P@$$word89@#"
        for username in usernames:
            initial_user_count = User.objects.count()
            response = self.client.post(reverse("signup"), {
            "username": username,
            "password1": good_password,
            "password2": good_password
            })
            # Test user count didn't increase, the user didn't get logged in, the page didn't get redirected (status code and template used), and the error message is correct.
            self.assertEqual(User.objects.count(), initial_user_count)
            self.assertFalse(response.wsgi_request.user.is_authenticated)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/signup.html")
            self.assertContains(response, "A user with that username already exists.")

    def test_user_signup_with_missing_fields(self):
        usernames = ["Randomuser27", ""]
        password1s = ["89%AJValidP@assword910", ""]
        password2s = ["89%AJValidP@assword910", ""]

        # Creates every combination of fields being present or not
        fields_combinations = product(usernames, password1s, password2s)
        
        # Test every combination of missing fields
        for username, password1, password2 in fields_combinations:
            # Pass when all fields are present because that would be testing a valid condition
            if username and password1 and password2:
                pass
            else:
                initial_user_count = User.objects.count()
                response = self.client.post(reverse("signup"), {
                    "username": username,
                    "password1": password1,
                    "password2": password2
                })
                # Test user count didn't increase, the user didn't get logged in, the page didn't get redirected (status code and template used).
                self.assertEqual(User.objects.count(), initial_user_count)
                self.assertFalse(response.wsgi_request.user.is_authenticated)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "accounts/signup.html")
                # Test for the correct error messages / elements, depending on which fields are missing.
                if not username:
                    self.assertContains(response, '<ul class="errorlist" id="id_username_error"><li>This field is required.</li></ul>')
                if not password1:
                    self.assertContains(response, '<ul class="errorlist" id="id_password1_error"><li>This field is required.</li></ul>')
                if not password2:
                    self.assertContains(response, '<ul class="errorlist" id="id_password2_error"><li>This field is required.</li></ul>')

    def test_user_signup_with_mismatched_passwords(self):
        initial_user_count = User.objects.count()
        response = self.client.post(reverse("signup"), {
            "username": "AnotherRandomUser890",
            "password1": "ARandom$$$Possword",
            "password2": "ARandom$Password"
        })
        # Test user count didn't increase, the user didn't get logged in, the page didn't get redirected (status code and template used), and the error message is correct.
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")
        self.assertContains(response, '<ul class="errorlist" id="id_password2_error"><li>The two password fields didn’t match.</li></ul>')

    def test_successful_user_signup(self):
        new_username = "AProgrammerMan"
        password = r'2}h~*%uLUl"G~[x.bIi~'

        initial_user_count = User.objects.count()
        response = self.client.post(reverse("signup"), {
            "username": new_username,
            "password1": password,
            "password2": password
        })

        # Test that the user count increased by exactly one, the account object with the new username exists in the database, the user is signed in, and the user is redirected to the dashboard.
        self.assertEqual(initial_user_count+1, User.objects.count())
        self.assertTrue(User.objects.filter(username=new_username).exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse("dashboard"))

    def test_user_is_redirected_when_already_logged_in(self):
        self.client.force_login(SignUpPageTests.user)
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("dashboard"))

        
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

        # Check nav bar content is appropriate for not being logged in
        TestHelper.assert_unauthenticated_nav(self, response)

        # Test the appropriate form content is present
        self.assertContains(response, '<label for="id_username">Username:</label>')
        self.assertContains(response, '<input type="text" name="username" autofocus autocapitalize="none" autocomplete="username" maxlength="150" required id="id_username">')
        self.assertContains(response, '<label for="id_password">Password:</label>')
        self.assertContains(response, '<input type="password" name="password" autocomplete="current-password" required id="id_password">')
        self.assertContains(response, '<button type="submit">Log In</button>')

        # Test for other page content
        self.assertContains(response, '<h2>Log In</h2>')
        self.assertContains(response, f'Don\'t have an account? <a href="{reverse("signup")}">Sign Up</a>')

        
class LogoutViewTests(TestCase):
    pass
