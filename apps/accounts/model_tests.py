from django.test import TestCase
from base.tests import TestHelper
from .models import UserAccount
from apps.finances.models import Category, EntryType
from decimal import Decimal
from django.contrib.auth import get_user_model





class UserAccountTests(TestCase):
    """Tests for the UserAccount model's methods."""

    def setUp(self):
        """Set up test users for each test."""
        self.user1 = get_user_model().objects.create_user(username="user1", password="password")
        self.user2 = get_user_model().objects.create_user(username="user2", password="password")

    def test_get_categories_returns_the_correct_categories(self):
        """
        Tests that the right number of categories is returned, and each category returned
        belongs to the correct user and has the correct name.
        """
        # Create test users
        user1 = self.user1
        user2 = self.user2
        
        # Create test info for each user
        user1_category_info = [
            (user1, "Food"),
            (user1, "Gas"),
            (user1, "Fun"),
        ]
        
        user2_category_info = [
            (user2, "Mortgage"),
            (user2, "Tools"),
            (user2, "Hunting"),
        ]

        # Create categories with test info, using EntryType.EXPENSE for all of them because that isn't being checked and leaving out optional fields.
        for cat_info in user1_category_info + user2_category_info:
            category = Category(
                user=cat_info[0],
                name=cat_info[1],
                entry_type = EntryType.EXPENSE
                )
            category.save()

        # Use the method that is being tested.
        user1_cats = user1.get_categories()
        user2_cats = user2.get_categories()
        
        # Check the correct number of categories is returned.
        self.assertEqual(len(user1_cats), len(user1_category_info))
        self.assertEqual(len(user2_cats), len(user2_category_info))

        # Check that the user and name of each category returned is correct for both users.
        for i in range(len(user1_category_info)):
            self.assertEqual(user1_cats[i].get_user(), user1_category_info[i][0])
            self.assertEqual(user1_cats[i].get_name(), user1_category_info[i][1])

        for i in range(len(user2_category_info)):
            self.assertEqual(user2_cats[i].get_user(), user2_category_info[i][0])
            self.assertEqual(user2_cats[i].get_name(), user2_category_info[i][1])


    def test_add_category_input_validation(self):
        """Tests the input validation for add_category. Written for the most part in the order of what add_category checks."""
        user1 = self.user1

        # Invalid type for name, valid EntryType, valid description
        with self.assertRaises(TypeError) as cm:
            user1.add_category(1, EntryType.EXPENSE, "Description")
        self.assertEqual(str(cm.exception), "name must be a string")

        # Valid name, valid entryType, omitted description, which should be valid
        starting_categories = len(user1.get_categories())
        user1.add_category("Valid Name", EntryType.EXPENSE)
        self.assertEqual(len(user1.get_categories()), starting_categories + 1)
        
        # Valid name, valid EntryType, invalid type for description
        with self.assertRaises(TypeError) as cm:
            user1.add_category("Good Name", EntryType.EXPENSE, 1)
        self.assertEqual(str(cm.exception), "description must be a string")

        # Name right at 50 character limit, valid EntryType, valid description
        starting_categories = len(user1.get_categories())
        user1.add_category("c"*50, EntryType.EXPENSE, "Valid description")
        self.assertEqual(len(user1.get_categories()), starting_categories + 1)

        # Name just over 50 character limit, valid EntryType, valid description
        with self.assertRaises(ValueError) as cm:
            user1.add_category("c"*51, EntryType.INCOME, "Valid description")

        # Valid name, valid EntryType, description right at 300 character limit
        starting_categories = len(user1.get_categories())
        user1.add_category("A new name", EntryType.INCOME, "c"*300)
        self.assertEqual(len(user1.get_categories()), starting_categories + 1)

        # Valid name, valid EntryType, description right over 300 character limit
        with self.assertRaises(ValueError) as cm:
            user1.add_category("An even newer name", EntryType.INCOME, "c"*301)
        
        # Valid name, incorrect entry_type input but string, valid description
        with self.assertRaises(ValueError) as cm:
            user1.add_category("Another name", "EntryType", "Description")

        # Valid everything, also using EntryType.INCOME this time
        starting_categories = len(user1.get_categories())
        user1.add_category("Last one", EntryType.INCOME, "A description")
        self.assertEqual(len(user1.get_categories()), starting_categories + 1)