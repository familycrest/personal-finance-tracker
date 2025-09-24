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

    def test_dashboard_exists_at_correct_url(self):
        self.client.force_login(DashboardPageTests.user)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_available_by_name(self):
        self.client.force_login(DashboardPageTests.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_is_correct(self):
        self.client.force_login(DashboardPageTests.user)
        response = self.client.get(reverse("dashboard"))
        self.assertTemplateUsed(response, "dashboard.html")

    def test_correct_content_shown_when_user_is_authenticated(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        self.client.force_login(DashboardPageTests.user)
        response = self.client.get(dashboard_url)

        # Test nav content is correct for being logged in
        self.assertContains(response, f'<a href="{home_url}">Home</a>')
        self.assertContains(response, f'<a href="{dashboard_url}">Dashboard</a>')
        self.assertContains(response, f'<button type="submit">Logout</button>')
        self.assertContains(
            response, f"Logged in as {DashboardPageTests.test_username}"
        )
        self.assertNotContains(response, f'<a href="{signup_url}">Signup</a>')
        self.assertNotContains(response, f'<a href="{login_url}">Login</a>')

        # Test main dashboard content is correct
        self.assertContains(response, "<h1>Dashboard</h1>")
        self.assertContains(response, f"Welcome, {DashboardPageTests.test_username}!")
        self.assertContains(
            response,
            "<p>Here you can track your budgets, expenses, and financial goals.</p>",
        )

    def test_dashboard_redirects_to_login_when_not_authenticated(self):
        expected_redirect_url = f"{reverse('login')}?next={reverse('dashboard')}"
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, expected_redirect_url)


class Custom404Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup user object for authenticated tests
        cls.test_username = "TestUser"
        cls.test_password = "Test0Password5601"
        cls.user = User.objects.create_user(
            username=cls.test_username, password=cls.test_password
        )

    def test_invalid_urls_use_correct_template(self):
        response = self.client.get("/non-existent-url")
        self.assertTemplateUsed(response, "404.html")
        response = self.client.get("/randomurl/sub_url_that_doesn't_exist")
        self.assertTemplateUsed(response, "404.html")
        response = self.client.get("/a_url/a_sub_url/a_further_sub_url")
        self.assertTemplateUsed(response, "404.html")

    def test_correct_content_shown_for_invalid_urls_when_not_authenticated(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        response = self.client.get("/random/url/thisIsInvalid")

        # Test nav content is correct for not being logged in
        self.assertContains(response, f'<a href="{home_url}">Home</a>', status_code=404)
        self.assertContains(response, f'<a href="{signup_url}">Signup</a>', status_code=404)
        self.assertContains(response, f'<a href="{login_url}">Login</a>', status_code=404)
        self.assertNotContains(response, f'<a href="{dashboard_url}">Dashboard</a>', status_code=404)
        self.assertNotContains(response, f'<button type="submit">Logout</button>', status_code=404)
        self.assertNotContains(response, f"Logged in as", status_code=404)

        # Test that main 404 page content is present
        self.assertContains(response, "<h1>Sorry, we couldn't find the page you were looking for...</h1>", status_code=404)
        self.assertContains(response, "<h3>404 Missing Page Error</h3>", status_code=404)
        self.assertContains(response, "<p>We couldn't find the page you were looking for.</p>", status_code=404)

    def test_correct_content_shown_for_invalid_urls_when_authenticated(self):
        home_url = reverse("home")
        signup_url = reverse("signup")
        login_url = reverse("login")
        dashboard_url = reverse("dashboard")

        self.client.force_login(Custom404Tests.user)
        response = self.client.get("/random/url/thisIsInvalid")

        # Test nav content is correct for being logged in
        self.assertContains(response, f'<a href="{home_url}">Home</a>', status_code=404)
        self.assertContains(response, f'<a href="{dashboard_url}">Dashboard</a>', status_code=404)
        self.assertContains(response, f'<button type="submit">Logout</button>', status_code=404)
        self.assertContains(response, f"Logged in as {Custom404Tests.test_username}", status_code=404)
        self.assertNotContains(response, f'<a href="{signup_url}">Signup</a>', status_code=404)
        self.assertNotContains(response, f'<a href="{login_url}">Login</a>', status_code=404)

        # Test that main 404 page content is present
        self.assertContains(response, "<h1>Sorry, we couldn't find the page you were looking for...</h1>", status_code=404)
        self.assertContains(response, "<h3>404 Missing Page Error</h3>", status_code=404)
        self.assertContains(response, "<p>We couldn't find the page you were looking for.</p>", status_code=404)