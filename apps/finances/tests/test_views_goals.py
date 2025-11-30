# Test file for goals views

from apps.finances.models import Category
from django.urls import reverse

from base.tests.test_base import TestHelper


class GoalViewsTests(TestHelper):
    def setUp(self):
        self.user, self.username, self.email = self.return_test_user()
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
        self.assertContains(response, f"Logged in as <strong>{self.username}</strong>")
        self.assertContains(
            response,
            "<h1>Account Goals</h1>",
        )

    def test_goals_page_content_unauthenticated(self):
        response = self.client.get(reverse("goals"))
        expected_redirect_url = f"{reverse('login')}?next={reverse('goals')}"
        self.assertRedirects(response, expected_redirect_url)
