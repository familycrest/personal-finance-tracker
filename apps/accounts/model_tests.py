from django.test import TestCase
from base.tests import TestHelper
from .models import UserAccount
from apps.finances.models import Category, EntryType
from decimal import Decimal
from django.contrib.auth import get_user_model





class UserAccountTests(TestCase):
    """Tests for the UserAccount model's methods."""

    def test_get_categories_returns_the_correct_categories(self):
        """
        Tests that the right number of categories is returned, and each category returned
        belongs to the correct user and has the correct name.
        """
        # Create test users
        user1 = get_user_model().objects.create_user(username="user1", password="password")
        user2 = get_user_model().objects.create_user(username="user2", password="password")
        
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