from django.test import TestCase
from django.urls import reverse


class SignUpPageTests(TestCase):
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
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        response = self.client.get(signup_url)

        # Test that the correct navigation links are present
        self.assertContains(response, f'<a href="{home_url}">Home</a>')
        self.assertContains(response, f'<a href="{signup_url}">Signup</a>')
        self.assertContains(response, f'<a href="{login_url}">Login</a>')
        # Test that the navigation for logged in users isn't present
        self.assertNotContains(response, f'<a href="{dashboard_url}">Dashboard</a>')
        self.assertNotContains(response, f'<button type="submit">Logout</button>')
        self.assertNotContains(response, f"Logged in as")

        # Test the form content
        


class LoginPageTests(TestCase):
    pass


class LogoutViewTests(TestCase):
    pass
