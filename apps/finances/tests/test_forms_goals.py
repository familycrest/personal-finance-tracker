# Test file for goals forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.finances.models import Category, AccountGoal, CategoryGoal
from apps.finances.forms import AddAccountGoalForm, AddCategoryGoalForm
from datetime import date
from calendar import monthrange
from decimal import Decimal


class GoalFormsTests(TestCase):
    def return_test_user(self):
        """Return user object and username for authenticated tests."""
        test_username = "TestUser"
        test_password = "Test0Password5601"
        user = get_user_model().objects.create_user(
            username=test_username, password=test_password
        )
        return user, test_username

    def setUp(self):
        self.user, self.username = self.return_test_user()
        self.category = Category.objects.create(user=self.user, name="Test Category")

    def test_add_account_goal_form_valid(self):
        form_data = {
            "name": "Account Goal",
            "description": "Test account goal",
            "entry_type": "EXPENSE",
            "time_length": "monthly",
            "amount": 300,
        }
        form = AddAccountGoalForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        account_goal = form.save()
        self.assertEqual(account_goal.user, self.user)
        self.assertEqual(account_goal.name, "Account Goal")
        self.assertEqual(account_goal.amount, 300)
        # Make sure the form amount inputted becomes a decimal.
        self.assertTrue(isinstance(account_goal.amount, Decimal))

    def test_add_category_goal_form_valid(self):
        form_data = {
            "category": self.category.id,
            "name": "Category Goal",
            "description": "Test category goal",
            "time_length": "monthly",
            "amount": 200,
        }
        form = AddCategoryGoalForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        category_goal = form.save()
        self.assertEqual(category_goal.category, self.category)
        self.assertEqual(category_goal.name, "Category Goal")
        self.assertEqual(category_goal.amount, 200)
        # Make sure the form amount inputted becomes a decimal.
        self.assertTrue(isinstance(category_goal.amount, Decimal))

    def test_add_account_goal_form_invalid_duplicate(self):
        # variables for the first and last date of current month
        start_date = date.today().replace(day=1)
        last_day = monthrange(start_date.year, start_date.month)[1]
        end_date = start_date.replace(day=last_day)

        # First, create an existing goal
        AccountGoal.objects.create(
            user=self.user,
            name="Existing Goal",
            entry_type="EXPENSE",
            start_date=start_date,
            end_date=end_date,
            amount=150,
        )
        form_data = {
            "user": self.user,
            "name": "Existing Goal",
            "description": "This should fail",
            "entry_type": "EXPENSE",
            "time_length": "monthly",
            "amount": 150,
        }

        form = AddAccountGoalForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "You already have an Expense goal for that time range.",
            form.errors["time_length"],
        )

    def test_add_category_goal_form_invalid_duplicate(self):
        # variables for the first and last date of current month
        start_date = date.today().replace(day=1)
        last_day = monthrange(start_date.year, start_date.month)[1]
        end_date = start_date.replace(day=last_day)

        # First, create a goal
        CategoryGoal.objects.create(
            category=self.category,
            name="Existing Category Goal",
            entry_type="EXPENSE",
            start_date=start_date,
            end_date=end_date,
            amount=250,
        )

        form_data = {
            "category": self.category,
            "name": "Existing Category Goal",
            "entry_type": "EXPENSE",
            "description": "This should fail",
            "time_length": "monthly",
            "amount": 250,
        }

        form = AddCategoryGoalForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "This category already has a goal for that time range.",
            form.errors["time_length"],
        )
