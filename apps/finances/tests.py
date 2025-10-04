from django.test import TestCase
from accounts.models import UserAccount
from finances.models import Category, Entry, EntryType
from datetime import date

# Create your tests here.

class CategoryModelTest(TestCase):

    def setUp(self):
        self.user = UserAccount.objects.create_user(username="testuser")
        
        self.category = Category.objects.create(
            user=self.user,
            name="Groceries",
            description="Monthly grocery shopping",
            entry_type=EntryType.EXPENSE
        )
        
        self.entry1 = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Walmart",
            description="Grocery shopping at Walmart",
            entry_type=EntryType.EXPENSE,
            date=date(2023, 10, 1),
            amount=150.00
        )
        
        self.entry2 = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Costco",
            description="Grocery shopping at Costco",
            entry_type=EntryType.EXPENSE,
            date=date(2023, 10, 5),
            amount=200.00
        )
        
        self.goal = self.category.add_goal(
            name="Monthly Grocery Budget",
            description="Limit grocery expenses to $400",
            entry_type=EntryType.EXPENSE,
            start_date=date(2023, 10, 1),
            end_date=date(2023, 10, 31),
            amount=400.00
        )
        
    def test_get_name(self):
        self.assertEqual(self.category.get_name(), "Groceries")
        
    def test_get_description(self):
        self.assertEqual(self.category.get_description(), "Monthly grocery shopping")
        
    def test_get_entry_type(self):
        self.assertEqual(self.category.get_entry_type(), EntryType.EXPENSE)
        
    def test_get_entries(self):
        entries = self.category.get_entries()
        self.assertEqual(entries.count(), 2)
        self.assertIn(self.entry1, entries)
        self.assertIn(self.entry2, entries)
        
    def test_add_entry(self):
        new_entry = self.category.add_entry(
            name="Trader Joe's",
            description="Grocery shopping at Trader Joe's",
            entry_type=EntryType.EXPENSE,
            date=date(2023, 10, 10),
            amount=75.00
        )
        entries = self.category.get_entries()
        self.assertEqual(entries.count(), 3)
        self.assertIn(new_entry, entries)
        
    def test_remove_entry(self):
        result = self.category.remove_entry(name="Walmart")
        entries = self.category.get_entries()
        self.assertTrue(result)
        self.assertEqual(entries.count(), 1)
        self.assertNotIn(self.entry1, entries)
        
    def test_get_goals(self):
        goals = self.category.get_goals()
        self.assertEqual(goals.count(), 1)
        self.assertIn(self.goal, goals)
        
    def test_add_goal(self):
        new_goal = self.category.add_goal(
            name="Weekly Grocery Budget",
            description="Limit weekly grocery expenses to $200",
            entry_type=EntryType.EXPENSE,
            start_date=date(2023, 10, 1),
            end_date=date(2023, 10, 7),
            amount=200.00
        )
        goals = self.category.get_goals()
        self.assertEqual(goals.count(), 2)
        self.assertIn(new_goal, goals)
        
    def test_remove_goal(self):
        result = self.category.remove_goal(name="Monthly Grocery Budget")
        goals = self.category.get_goals()
        self.assertTrue(result)
        self.assertEqual(goals.count(), 0)
        self.assertNotIn(self.goal, goals)
        
    def test_get_total(self):
        total = self.category.get_total()
        self.assertEqual(total, 350.00)
    
    def test_get_goal_percentage_one_goal(self):
        percentages = self.category.get_goal_percentage()
        self.assertIn(self.goal, percentages)
        self.assertEqual(percentages[self.goal], 87.5)  # (350/400)*100 = 87.5%
        
    def test_get_goal_percentage_multiple_goals(self):
        second_goal = self.category.add_goal(
            name="Extra Grocery Budget",
            description="Extra budget for groceries",
            entry_type=EntryType.EXPENSE,
            start_date=date(2023, 10, 1),
            end_date=date(2023, 10, 31),
            amount=300.00
        )
        percentages = self.category.get_goal_percentage()
        self.assertIn(self.goal, percentages)
        self.assertIn(second_goal, percentages)
        self.assertEqual(percentages[self.goal], 87.5)  # (350/400)*100 = 87.5%
        self.assertEqual(percentages[second_goal], 100.0)  # (350/300)*100 = 116.67% capped at 100%
    
    def test_get_goal_percentage_no_goals(self):
        self.category.remove_goal(name="Monthly Grocery Budget")
        percentages = self.category.get_goal_percentage()
        self.assertEqual(percentages, {})  # No goals set
    
    
class EntryModelTest(TestCase):

    def setUp(self):
        self.user = UserAccount.objects.create_user(username="testuser")
        
        self.category = Category.objects.create(
            user=self.user,
            name="Salary",
            description="Monthly salary income"
        )
        
        self.entry = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="October Salary",
            description="Salary for October 2023",
            entry_type=EntryType.INCOME,
            date=date(2023, 10, 1),
            amount=5000.00
        )
        
    def test_entry_creation(self):
        self.assertEqual(self.entry.name, "October Salary")
        self.assertEqual(self.entry.description, "Salary for October 2023")
        self.assertEqual(self.entry.entry_type, EntryType.INCOME)
        self.assertEqual(self.entry.date, date(2023, 10, 1))
        self.assertEqual(self.entry.amount, 5000.00)
        self.assertEqual(self.entry.category, self.category)
        self.assertEqual(self.entry.user, self.user)