from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class TestHelper:
    """A class to run tests on the header content and setup the test user for other test classes."""

    @staticmethod
    def return_test_user():
        """Return user object and username for authenticated tests."""
        test_username = "TestUser"
        test_password = "Test0Password5601"
        user = User.objects.create_user(username=test_username, password=test_password)
        return user, test_username

    @staticmethod
    def assert_unauthenticated_header(test_case, response, http_code=200):
        # The http code parameter is necessary for instances such as testing the header in the custom 404 view.
        # assert will throw an error if the code isn't 200 unless a code is specified.
        """Test the header's contents when the user isn't logged in. This method checks the entire page for these elements, not just the header element."""

        # Home, signup, and login links.
        expected = [
            f'<a href="{reverse("home")}">Home</a>',
            f'<a href="{reverse("signup")}">Signup</a>',
            f'<a href="{reverse("login")}">Login</a>',
        ]

        # Dashboard link, logout button, "Logged in as {username}"
        unexpected = [
            f'<a href="{reverse("dashboard")}">Dashboard</a>',
            '<button type="submit">Logout</button>',
            "Logged in as",
        ]
        for element in expected:
            test_case.assertContains(response, element, status_code=http_code)

        for element in unexpected:
            test_case.assertNotContains(response, element, status_code=http_code)

    def assert_authenticated_header(test_case, response, username, http_code=200):
        """Test the header's contents when the user is logged in. This method checks the entire page for these elements, not just the header element."""
        # Home and dashboard links, logout button, "Logged in as {username}" element
        expected = [
            f'<a href="{reverse("home")}">Home</a>',
            f'<a href="{reverse("dashboard")}">Dashboard</a>',
            '<button type="submit">Logout</button>',
            f"Logged in as {username}",
        ]
        # Signup and login links
        unexpected = [
            f'<a href="{reverse("signup")}">Signup</a>',
            f'<a href="{reverse("login")}">Login</a>',
        ]

        for element in expected:
            test_case.assertContains(response, element, status_code=http_code)

        for element in unexpected:
            test_case.assertNotContains(response, element, status_code=http_code)


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Fetch test user for authenticated tests
        cls.user, cls.username = TestHelper.return_test_user()

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
        response = self.client.get(reverse("home"))

        # Test header content is correct for not being logged in
        TestHelper.assert_unauthenticated_header(self, response)

        # Test the main content of the home page is there
        self.assertContains(response, "<h1>Welcome to My Finance Tracker!</h1>")
        self.assertContains(
            response,
            "Track your personal finances, budgets, and expenses all in one place.",
        )

    def test_correct_content_shown_when_user_is_authenticated(self):
        self.client.force_login(HomePageTests.user)
        response = self.client.get(reverse("home"))

        # Test header content is correct for being logged in
        TestHelper.assert_authenticated_header(self, response, HomePageTests.username)

        # Test the main content of the home page is there
        self.assertContains(response, "<h1>Welcome to My Finance Tracker!</h1>")
        self.assertContains(
            response,
            "Track your personal finances, budgets, and expenses all in one place.",
        )


class DashboardPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Fetch test user for authenticated tests
        cls.user, cls.username = TestHelper.return_test_user()

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
        self.client.force_login(DashboardPageTests.user)
        response = self.client.get(reverse("dashboard"))

        # Test header content is correct for being logged in
        TestHelper.assert_authenticated_header(
            self, response, DashboardPageTests.username
        )

        # Test main dashboard content is correct
        self.assertContains(response, "<h1>Dashboard</h1>")
        self.assertContains(response, f"Welcome, {DashboardPageTests.username}!")
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
        # Fetch test user for authenticated tests
        cls.user, cls.username = TestHelper.return_test_user()

    def test_invalid_urls_use_correct_template(self):
        response = self.client.get("/non-existent-url")
        self.assertTemplateUsed(response, "404.html")
        response = self.client.get("/randomurl/sub_url_that_doesn't_exist")
        self.assertTemplateUsed(response, "404.html")
        response = self.client.get("/a_url/a_sub_url/a_further_sub_url")
        self.assertTemplateUsed(response, "404.html")

    def test_correct_content_shown_for_invalid_urls_when_not_authenticated(self):
        response = self.client.get("/random/url/thisIsInvalid")

        # Test header content is correct for not being logged in
        TestHelper.assert_unauthenticated_header(self, response, 404)

        # Test that main 404 page content is present
        self.assertContains(
            response,
            "<h1>Sorry, we couldn't find the page you were looking for...</h1>",
            status_code=404,
        )
        self.assertContains(
            response, "<h3>404 Missing Page Error</h3>", status_code=404
        )
        self.assertContains(
            response,
            "<p>We couldn't find the page you were looking for.</p>",
            status_code=404,
        )

    def test_correct_content_shown_for_invalid_urls_when_authenticated(self):
        self.client.force_login(Custom404Tests.user)
        response = self.client.get("/random/url/thisIsInvalid")

        # Test header content is correct for being logged in
        TestHelper.assert_authenticated_header(
            self, response, Custom404Tests.username, 404
        )

        # Test that main 404 page content is present
        self.assertContains(
            response,
            "<h1>Sorry, we couldn't find the page you were looking for...</h1>",
            status_code=404,
        )
        self.assertContains(
            response, "<h3>404 Missing Page Error</h3>", status_code=404
        )
        self.assertContains(
            response,
            "<p>We couldn't find the page you were looking for.</p>",
            status_code=404,
        )
