from datetime import date, timedelta
import calendar

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.finances.models import Category, CategoryGoal, EntryType


User = get_user_model()


# Returns correct date range for the current week
def get_current_week_range(today=None):
    if today is None:
        today = date.today()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week


# Returns correct date range for the current month
def get_current_month_range(today=None):
    if today is None:
        today = date.today()

    start_of_month = date(today.year, today.month, 1)
    last_day_in_month = calendar.monthrange(today.year, today.month)[1]
    end_of_month = date(today.year, today.month, last_day_in_month)

    return start_of_month, end_of_month


# Returns correct date range for the current year
def get_current_year_range(today=None):
    if today is None:
        today = date.today()

    start_of_year = date(today.year, 1, 1)
    end_of_year = date(today.year, 12, 31)

    return start_of_year, end_of_year


class CategoriesViewTests(TestCase):
    # Testing data that all tests will use
    @classmethod
    def setUpTestData(cls):
        # Create two users for uniqueness testing
        cls.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="testPass1!?!?",
        )
        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testPass2!?!?",
        )

        # Create base categories for both users
        cls.user1_income = Category.objects.create(
            user=cls.user1,
            name="Salary",
            entry_type=EntryType.INCOME,
        )

        cls.user1_expense = Category.objects.create(
            user=cls.user1,
            name="Food",
            entry_type=EntryType.EXPENSE,
        )

        cls.user2_expense = Category.objects.create(
            user=cls.user2,
            name="Food",
            entry_type=EntryType.EXPENSE,
        )

        # Create three category goals to test
        week_start, week_end = get_current_week_range()
        month_start, month_end = get_current_month_range()
        year_start, year_end = get_current_year_range()

        # Weekly category goal
        cls.user1_food_week_goal = CategoryGoal.objects.create(
            category=cls.user1_expense,
            name="Food Budget",
            description="Weekly food budget",
            entry_type=EntryType.EXPENSE,
            start_date=week_start,
            end_date=week_end,
            amount=100,
        )

        # Monthly category goal
        cls.user1_food_month_goal = CategoryGoal.objects.create(
            category=cls.user1_expense,
            name="Food Budget",
            description="Monthly food budget",
            entry_type=EntryType.EXPENSE,
            start_date=month_start,
            end_date=month_end,
            amount=400,
        )

        # Yearly category goal
        cls.user1_food_year_goal = CategoryGoal.objects.create(
            category=cls.user1_expense,
            name="Food Budget",
            description="Monthly food budget",
            entry_type=EntryType.EXPENSE,
            start_date=year_start,
            end_date=year_end,
            amount=4800,
        )

        # URL going directly to categories page
        cls.categories_url = reverse("categories")

    def setUp(self):
        self.client.force_login(user=self.user1)

    def test_categories_requires_authentication(self):
        """Anonymous users should be redirected when accessing the categories page."""
        self.client.logout()
        response = self.client.get(self.categories_url)

        self.assertEqual(response.status_code, 302)

    def test_categories_shows_only_logged_in_users_categories(self):
        """Categories view should show categories for the logged-in user only."""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, 200)

        html = response.content.decode("utf-8")

        # User1's categories should be visible
        self.assertIn("/finances/categories/delete/1/", html)
        self.assertIn("/finances/categories/delete/2/", html)

        # User2's category should not be visible
        self.assertNotIn("finances/categories/delete/3", html)

    def test_weekly_period_renders_page_with_goals(self):
        """When period=weekly, the page still renders and shows the weekly goal."""
        response = self.client.get(self.categories_url, {"period": "weekly"})
        self.assertEqual(response.status_code, 200)

        html = response.content.decode("utf-8")
        self.assertIn("$100.00", html)

    def test_monthly_period_renders_page_with_goals(self):
        """When period=monthly, the page renders and shows the monthly goal."""
        response = self.client.get(self.categories_url, {"period": "monthly"})
        self.assertEqual(response.status_code, 200)

        html = response.content.decode("utf-8")
        self.assertIn("$400.00", html)

    def test_yearly_period_renders_page_with_goals(self):
        """When period=yearly, the page renders and shows the yearly goal."""
        response = self.client.get(self.categories_url, {"period": "yearly"})
        self.assertEqual(response.status_code, 200)

        html = response.content.decode("utf-8")
        self.assertIn("$4800.00", html)
