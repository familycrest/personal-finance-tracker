# Tests for Goal, AccountGoal, and CategoryGoal models
from django.core.exceptions import ValidationError
from apps.finances.models import AccountGoal, CategoryGoal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.finances.models import Category


class GoalModelTests(TestCase):
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

    #  Only test account goal and category goal, not the abstract Goal model
    # Use the models as they appear in the comment above to guide the tests
    # do not use fields that do not exist in the models such as target_amount
    # do not call Goal directly since it is abstract
    def test_create_account_goal(self):
        account_goal = AccountGoal.objects.create(
            user=self.user,
            name="Account Goal",
            entry_type="EXPENSE",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=300,
        )
        self.assertEqual(account_goal.user, self.user)
        self.assertEqual(account_goal.name, "Account Goal")
        self.assertEqual(account_goal.entry_type, "EXPENSE")
        self.assertEqual(account_goal.amount, 300)

    def test_create_category_goal(self):
        category_goal = CategoryGoal.objects.create(
            category=self.category,
            name="Category Goal",
            entry_type="INCOME",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=200,
        )
        self.assertEqual(category_goal.category, self.category)
        self.assertEqual(category_goal.name, "Category Goal")
        self.assertEqual(category_goal.amount, 200)

    def test_account_goal_string_representation(self):
        account_goal = AccountGoal.objects.create(
            user=self.user,
            name="Account String Rep",
            entry_type="EXPENSE",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=600,
        )
        self.assertEqual(str(account_goal), "Account String Rep")

    def test_category_goal_string_representation(self):
        category_goal = CategoryGoal.objects.create(
            category=self.category,
            name="Category String Rep",
            entry_type="INCOME",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=700,
        )
        self.assertEqual(str(category_goal), "Category String Rep (Test Category)")

    def test_account_goal_validation(self):
        with self.assertRaises(ValidationError):
            account_goal = AccountGoal(
                user=self.user,
                name="",
                entry_type="EXPENSE",
                start_date="2024-01-01",
                end_date="2024-12-31",
                amount=-50,
            )
            account_goal.full_clean()  # This will raise ValidationError

    def test_category_goal_validation(self):
        with self.assertRaises(ValidationError):
            category_goal = CategoryGoal(
                category=self.category,
                name="",
                entry_type="INCOME",
                start_date="2024-01-01",
                end_date="2024-12-31",
                amount=-75,
            )
            category_goal.full_clean()  # This will raise ValidationError

    def test_create_goal(self):
        account_goal = AccountGoal.objects.create(
            user=self.user,
            name="Test Goal",
            entry_type="EXPENSE",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=500,
        )
        self.assertEqual(account_goal.name, "Test Goal")
        self.assertEqual(account_goal.amount, 500)
        category_goal = CategoryGoal.objects.create(
            category=self.category,
            name="Test Goal",
            entry_type="INCOME",
            start_date="2024-01-01",
            end_date="2024-12-31",
            amount=500,
        )
        self.assertEqual(category_goal.name, "Test Goal")
        self.assertEqual(category_goal.amount, 500)

    def test_goal_validation(self):
        with self.assertRaises(ValidationError):
            account_goal = AccountGoal(
                user=self.user,
                name="",
                entry_type="EXPENSE",
                start_date="2024-01-01",
                end_date="2024-12-31",
                amount=-100,
            )
            account_goal.full_clean()  # This will raise ValidationError
        with self.assertRaises(ValidationError):
            category_goal = CategoryGoal(
                category=self.category,
                name="",
                entry_type="INCOME",
                start_date="2024-01-01",
                end_date="2024-12-31",
                amount=-100,
            )
            category_goal.full_clean()  # This will raise ValidationError
