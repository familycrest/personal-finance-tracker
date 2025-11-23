from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.finances.models import Category, EntryType
from apps.finances.forms import CategoryForm


User = get_user_model()


class CategoryFormTests(TestCase):
    # Testing data that all tests will use
    @classmethod
    def setUpTestData(cls):
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

        cls.user2_misc = Category.objects.create(
            user=cls.user2,
            name="Misc.",
            entry_type=EntryType.EXPENSE,
        )

    # Method to create form instance
    def make_form(self, data=None, instance=None, user=None):
        # The user for most of the tests is user1, so set default to user1
        if user is None:
            user = self.user1

        return CategoryForm(data=data, instance=instance, user=user)

    def test_create_valid_category_for_user(self):
        """Should create a valid category for user1."""
        form = self.make_form(
            data={
                "name": "Rent",
                "entry_type": EntryType.EXPENSE,
            },
            user=self.user1,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_name_for_same_user_invalid(self):
        """Should raise error when making duplicate category name for same user."""
        form = self.make_form(
            data={
                "name": "food",  # should be case-insensitive
                "entry_type": EntryType.EXPENSE,
            },
            user=self.user1,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_same_name_for_different_user_valid(self):
        """Should create valid category with duplicate name for a separate user."""
        form = self.make_form(
            data={
                "name": "Food",
                "entry_type": EntryType.EXPENSE,
            },
            user=self.user2,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_keeps_entry_type_locked(self):
        """
        Should keep entry_type the same as when
        created if user somehow tries to edit it.
        """
        form = self.make_form(
            data={
                "name": "Food",
                "entry_type": EntryType.INCOME,  # user tries to change
            },
            instance=self.user1_expense,
            user=self.user1,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["entry_type"],
            EntryType.EXPENSE,  # locked to original
        )
