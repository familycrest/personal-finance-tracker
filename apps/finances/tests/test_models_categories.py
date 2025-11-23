from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.finances.models import Category, EntryType


User = get_user_model()


class CategoryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Testing data that all tests will use"""

        # Create two users for uniqueness testing
        cls.user1 = User.objects.create_user(
            username="testuser1",
            password="testPass1!?!?",
            email="testuser1@example.com",
        )
        cls.user2 = User.objects.create_user(
            username="testuser2",
            password="testPass2!?!?",
            email="testuser2@example.com",
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

    def test_str_returns_name(self):
        """__str__ should return just the category's name."""
        self.assertEqual(str(self.user1_income), "Salary")
        self.assertEqual(str(self.user1_expense), "Food")

    def test_description_is_optional(self):
        """Category should be valid when description is not given."""
        cat = Category(
            user=self.user1,
            name="No Description",
            entry_type=EntryType.EXPENSE,
            # Don't give a description field
        )

        # If any field requirements invalid, raises error
        cat.full_clean()

    def test_same_cat_name_allowed_between_different_users(self):
        """Identical category names should be able to exist for different users."""
        food = Category.objects.filter(name="Food")
        self.assertEqual(food.count(), 2)

        users = {c.user for c in food}
        self.assertIn(self.user1, users)
        self.assertIn(self.user2, users)

    def test_same_name_not_allowed_for_same_user(self):
        """Duplicate names should not be able to exist for the same user."""
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                user=self.user1,
                name="Salary",
                entry_type=EntryType.INCOME,
            )

    def test_entry_type_must_be_valid_choice(self):
        """entry_type should not be anything other than INCOME or EXPENSE."""
        cat = Category(
            user=self.user1,
            name="Invalid Type",
            entry_type="INVALID_TYPE",
        )
        with self.assertRaises(Exception):
            # If invalid, raise error
            cat.full_clean()
