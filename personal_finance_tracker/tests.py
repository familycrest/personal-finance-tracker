from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup user object for authenticated tests
        cls.test_username = "TestUser"
        cls.test_password = "Test0Password5601"
        cls.user = User.objects.create_user(
            username=cls.test_username, password=cls.test_password
        )

    def test_home_page_at_correct_url(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_available_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_is_correct(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")

    def test_correct_content_shown_when_user_not_authenticated(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        response = self.client.get(home_url)

        # Test nav content is correct for not being logged in
        self.assertContains(response, f'<a href="{home_url}">Home</a>')
        self.assertContains(response, f'<a href="{signup_url}">Signup</a>')
        self.assertContains(response, f'<a href="{login_url}">Login</a>')
        self.assertNotContains(response, f'<a href="{dashboard_url}">Dashboard</a>')
        self.assertNotContains(response, f'<button type="submit">Logout</button>')
        self.assertNotContains(response, f"Logged in as")

        # Test the main content of the home page is there
        self.assertContains(response, "<h1>Welcome to My Finance Tracker!</h1>")
        self.assertContains(
            response,
            "Track your personal finances, budgets, and expenses all in one place.",
        )

    def test_correct_content_shown_when_user_is_authenticated(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        self.client.force_login(HomePageTests.user)
        response = self.client.get(home_url)

        # Test nav content is correct for being logged in
        self.assertContains(response, f'<a href="{home_url}">Home</a>')
        self.assertContains(response, f'<a href="{dashboard_url}">Dashboard</a>')
        self.assertContains(response, f'<button type="submit">Logout</button>')
        self.assertContains(response, f"Logged in as {HomePageTests.test_username}")
        self.assertNotContains(response, f'<a href="{signup_url}">Signup</a>')
        self.assertNotContains(response, f'<a href="{login_url}">Login</a>')

        # Test the main content of the home page is there
        self.assertContains(response, "<h1>Welcome to My Finance Tracker!</h1>")
        self.assertContains(
            response,
            "Track your personal finances, budgets, and expenses all in one place.",
        )

    class DashboardPageTests(TestCase):
        @classmethod
        def setUpTestData(cls):
            # Setup user object for authenticated tests
            cls.test_username = "TestUser"
            cls.test_password = "Test0Password5601"
            cls.user = User.objects.create_user(
                username=cls.test_username, password=cls.test_password
            )

        
        