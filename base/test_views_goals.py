# Test file for goals views

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.finances.models import Category
from .test_models_goals import GoalModelTests
from django.urls import reverse


class GoalViewsTests(TestCase):
    def return_test_user():
        """Return user object and username for authenticated tests."""
        test_username = "TestUser"
        test_password = "Test0Password5601"
        user = get_user_model().objects.create_user(
            username=test_username, password=test_password
        )
        return user, test_username

    def setUp(self):
        self.user, self.username = GoalModelTests.return_test_user()
        self.category = Category.objects.create(user=self.user, name="Test Category")

    def test_goals_page_accessible_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("goals"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finances/goals.html")

    def test_goals_page_redirects_unauthenticated(self):
        response = self.client.get(reverse("goals"))
        expected_redirect_url = f"{reverse('login')}?next={reverse('goals')}"
        self.assertRedirects(response, expected_redirect_url)

    def test_goals_page_content_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("goals"))
        self.assertContains(response, "Goals")
        self.assertContains(response, f"Logged in as {self.username}")
        self.assertContains(
            response,
            "<h2>Account Goals</h2>",
        )

    def test_goals_page_content_unauthenticated(self):
        response = self.client.get(reverse("goals"))
        expected_redirect_url = f"{reverse('login')}?next={reverse('goals')}"
        self.assertRedirects(response, expected_redirect_url)
