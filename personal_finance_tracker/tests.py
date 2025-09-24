from django.test import SimpleTestCase
from django.test.utils import setup_test_environment
from django.urls import reverse

class HomePageTests(SimpleTestCase):
    def test_home_page_at_correct_url(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_available_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_is_correct(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")

    def test_correct_content_shown(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")

        response = self.client.get(home_url)
        self.assertContains(response, "<h1>Welcome to My Finance Tracker!</h1>")
        self.assertContains(response, f'<a href="{home_url}">Home</a>')
        self.assertContains(response, f'<a href="{signup_url}">Signup</a>')
        self.assertContains(response, f'<a href="{login_url}">Login</a>')
        self.assertContains(response, "Track your personal finances, budgets, and expenses all in one place.")


#class DashboardPageTests(SimpleTestCase):