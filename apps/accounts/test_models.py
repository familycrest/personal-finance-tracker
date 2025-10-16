from django.test import TestCase
from apps.finances.models import Category, EntryType
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from datetime import date





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

    
    def test_category_is_created_with_correct_data(self):
        """Test that the category is created with the right data for the right user and only one user."""

        # Create test users
        user1 = self.user1
        user2 = self.user2

        # Create data for each user
        user1_category_data = [
            ("name1", EntryType.EXPENSE, "Desc1"),
            ("name2", EntryType.EXPENSE, "Desc2"),
            ("name3", EntryType.INCOME, "Desc3"),
            ("name4", EntryType.INCOME, "Desc4"),
        ]

        user2_category_data = [
            ("name5", EntryType.EXPENSE, "Desc5"),
            ("name6", EntryType.EXPENSE, "Desc6"),
            ("name7", EntryType.INCOME, "Desc7"),
            ("name8", EntryType.INCOME, "Desc8"),
        ]

        # Create categories for each user
        for cat in user1_category_data:
            user1.add_category(cat[0], cat[1], cat[2])

        for cat in user2_category_data:
            user2.add_category(cat[0], cat[1], cat[2])

        user1_cats = user1.get_categories()
        user2_cats = user2.get_categories()

        # Test all the user1 categories are in user 1 and correct
        for i, cat in enumerate(user1_category_data):
            self.assertEqual(user1_cats[i].get_user(), user1)
            self.assertEqual(user1_cats[i].get_name(), cat[0])
            self.assertEqual(user1_cats[i].get_entry_type(), cat[1])
            self.assertEqual(user1_cats[i].get_description(), cat[2])

        # Test all the user 2 categories are in user 2 and correct
        for i, cat in enumerate(user2_category_data):
            self.assertEqual(user2_cats[i].get_user(), user2)
            self.assertEqual(user2_cats[i].get_name(), cat[0])
            self.assertEqual(user2_cats[i].get_entry_type(), cat[1])
            self.assertEqual(user2_cats[i].get_description(), cat[2])

    
    def test_remove_category_removes_correct_category(self):
        """Test that the correct category gets removed."""
        user1 = self.user1
        test_cats = []
        removed_test_cats = []
        
        # Tests every category in removed_test_cats isn't present in user1.get_categories()
        # Tests every remaining category IS present
        def check_for_categories():
            user_cats = user1.get_categories()
            for test_cat in test_cats:
                if test_cat not in removed_test_cats:
                    self.assertIn(test_cat, user_cats)
                else:
                    self.assertNotIn(test_cat, user_cats)

        # Create test categories
        for i in range(3):
            cat = user1.add_category(f"Name{i+1}", EntryType.EXPENSE, "Desc")
            test_cats.append(cat)

        # Check all created categories are present in user1.get_categories() then test each one gets removed properly.
        check_for_categories()
        for i in test_cats:
            user1.remove_category(i.get_name())
            removed_test_cats.append(i)
            check_for_categories()

    def test_remove_category_returns_correct_category(self):
        """Test that the removed category object gets returned."""
        user1 = self.user1

        # Create test category and assert it was added
        test_cat = user1.add_category("Name1", EntryType.EXPENSE, "Desc")
        self.assertIn(test_cat, user1.get_categories())

        # Get category returned by the user and assert it was removed
        returned_category = user1.remove_category(test_cat.get_name())
        self.assertNotIn(test_cat, user1.get_categories())

        # Convert the model objects to dicts without the id because it gets removed when the object
        # is deleted, then make sure the values are equal. The second line probably doesn't need exclude.
        test_cat_fields = model_to_dict(test_cat, exclude=['id'])
        returned_cat_fields = model_to_dict(returned_category, exclude=['id'])
        self.assertEqual(test_cat_fields, returned_cat_fields)

    def test_get_entries(self):
        user1 = self.user1
        category1 = user1.add_category("category", EntryType.EXPENSE, "test category")
        category1.add_entry("Expense1", "Kayak", EntryType.EXPENSE, date(2025, 10, 15), Decimal("1000"))
        category1.add_entry("Expense2", "Really big boat", EntryType.EXPENSE, date(2025, 11, 15), Decimal("10000"))
        category2 = user1.add_category("category2", EntryType.INCOME, "test category 2")
        category2.add_entry("Income", "Paycheck", EntryType.INCOME, date(2025, 10, 15), Decimal("5000"))


        # Test get income entries
        income_entries = user1.get_entries(EntryType.INCOME)
        self.assertEqual(len(income_entries), 1)
        self.assertTrue(income_entries[0].get_name(), "Income")

        # Test get expense entries
        expense_entries = user1.get_entries(EntryType.EXPENSE)
        self.assertEqual(len(expense_entries), 2)


        # Test get income entries in date range

        # Test start_date > end_date returns error

        # Assert incorrect value for entry_type raises a value error
        with self.assertRaises(ValueError):
            user1.get_entries("whatever")
        
        # Assert the wrong attribute for EntryType.whatever raises an attribute error
        with self.assertRaises(AttributeError):
            user1.get_entries(EntryType.INVALID)