# Testing goals history model
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Goal, AccountGoal, CategoryGoal, Category, EntryType, Entry
from datetime import date

User = get_user_model()
       
class GoalHistoryModelTest(TestCase):
    def setUp(self):
        # clean up all tables before each test
        User.objects.all().delete()
        Category.objects.all().delete()
        AccountGoal.objects.all().delete()
        CategoryGoal.objects.all().delete()


        self.user = User.objects.create_user(
            username="testuser", email="testexample@gmail.com", password="testpassword"
        )
        self.category = Category.objects.create(
            user=self.user,
            name="Test Category",
            entry_type=EntryType.INCOME,
        )
        self.account_goal = AccountGoal.objects.create(
            user=self.user,
            name="Test Account Goal",
            amount=1000.00,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 12, 31),
        )

        self.category_goal = CategoryGoal.objects.create(
            category=self.category,
            name="Test Category Goal",
            amount=500.00,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

    def test_account_goal_creation(self):
        self.assertEqual(self.account_goal.user, self.user)
        self.assertEqual(self.account_goal.name, "Test Account Goal")
        self.assertEqual(self.account_goal.amount, 1000.00)
        self.assertEqual(self.account_goal.start_date, date(2022, 1, 1))
        self.assertEqual(self.account_goal.end_date, date(2022, 12, 31))

    def test_category_goal_creation(self):
        self.assertEqual(self.category_goal.category, self.category)
        self.assertEqual(self.category_goal.name, "Test Category Goal")
        self.assertEqual(self.category_goal.amount, 500.00)
        self.assertEqual(self.category_goal.start_date, date(2025, 1, 1))
        self.assertEqual(self.category_goal.end_date, date(2025, 6, 30))

    def test_category_goal_entry_type_auto_set(self):
        self.assertEqual(self.category_goal.entry_type, self.category.entry_type)

    # def test_account_goal_progress(self):
    #     # Create entries that contribute to the account goal
    #     Entry.objects.create(
    #         name="Test Entry 1",
    #         user=self.user,
    #         entry_type=EntryType.INCOME,
    #         amount=200.00,
    #         date=date(2023, 3, 15),
    #     )
    #     Entry.objects.create(
    #         name="Test Entry 2",
    #         user=self.user,
    #         entry_type=EntryType.INCOME,
    #         amount=300.00,
    #         date=date(2023, 5, 20),
    #     )

    #     progress = self.account_goal.progress
    #     self.assertEqual(progress, 50.0)  # (200 + 300) / 1000 * 100 = 50%

    # def test_category_goal_progress(self):
    #     # create new category for 2023
    #     self.category_2023 = Category.objects.create(
    #         user=self.user,
    #         name="Test Category 2023",
    #         entry_type=EntryType.INCOME,
    #     )
    #     self.category_goal_2023 = CategoryGoal.objects.create(
    #         category=self.category_2023,
    #         name="Test Category Goal 2023",
    #         amount=500.00,
    #         start_date=date(2023, 1, 1),
    #         end_date=date(2023, 6, 30),
    #     )


    #     # Create entries that contribute to the category goal
    #     Entry.objects.create(
    #         name="Test Entry 3",
    #         user=self.user,
    #         category=self.category_2023,
    #         entry_type=self.category_2023.entry_type,
    #         amount=150.00,
    #         date=date(2023, 2, 10),
    #     )
    #     Entry.objects.create(
    #         name="Test Entry 4",
    #         user=self.user,
    #         category=self.category_2023,
    #         entry_type=self.category_2023.entry_type,
    #         amount=100.00,
    #         date=date(2023, 4, 5),
    #     )

    #     progress = self.category_goal.progress()
    #     self.assertEqual(self.category_goal.amount, 500.00)
    #     self.assertEqual(progress, 50.0)  # (150 + 100) / 500 * 100 = 50%

    def test_goal_progress_with_no_entries(self):
        progress = self.account_goal.progress
        self.assertEqual(progress, 0.0)

        progress = self.category_goal.progress
        self.assertEqual(progress, 0.0)

    def test_goal_progress_with_zero_amount(self):
        zero_amount_goal = AccountGoal.objects.create(
            user=self.user,
            name="Zero Amount Goal",
            amount=0.00,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        progress = zero_amount_goal.progress
        self.assertIsNone(progress)
        zero_amount_cat_goal = CategoryGoal.objects.create(
            category=self.category,
            name="Zero Amount Category Goal",
            amount=0.00,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 30),
        )   
        progress = zero_amount_cat_goal.progress
        self.assertIsNone(progress)

# Test goal history view and template
class GoalHistoryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username="testuser", email="example@gmail.com", password="testpassword"
        )

    def test_goal_history_view_redirects_when_not_logged_in(self):
        response = self.client.get(reverse("goal_history"))
        expected_redirect_url = f"{reverse('login')}?next={reverse('goal_history')}"
        self.assertRedirects(response, expected_redirect_url)

    def test_goal_history_view_loads_correct_template_when_logged_in(self):
        self.client.force_login(GoalHistoryViewTests.user)
        response = self.client.get(reverse("goal_history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finances/goal_history.html")

    def test_goal_history_view_context_data(self):
        self.client.force_login(GoalHistoryViewTests.user)
        response = self.client.get(reverse("goal_history"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("goals_output", response.context)

        # Since no goals exist yet, the list should be empty
        self.assertEqual(len(response.context["goals_output"]), 0)
    def test_goal_history_view_with_goals(self):
        self.client.force_login(GoalHistoryViewTests.user)

        # Create some goals for the user
        AccountGoal.objects.create(
            user=GoalHistoryViewTests.user,
            name="Test Account Goal 1",
            amount=1000.00,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
        )
        category = Category.objects.create(
            user=GoalHistoryViewTests.user,
            name="Test Category",
            entry_type=EntryType.EXPENSE,
        )
        CategoryGoal.objects.create(
            category=category,
            name="Test Category Goal 1",
            amount=500.00,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 30),
        )

        response = self.client.get(reverse("goal_history"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("goals_output", response.context)

        # Now the list should contain 2 goals
        self.assertEqual(len(response.context["goals_output"]), 2)
        goal_names = [goal["name"] for goal in response.context["goals_output"]]
        self.assertIn("Test Account Goal 1", goal_names)
        self.assertIn("Test Category Goal 1", goal_names)

        # Check that category name is included for CategoryGoal
        for goal in response.context["goals_output"]:
            if goal["name"] == "Test Category Goal 1":
                self.assertEqual(goal["category_name"], "Test Category")
            else:
                self.assertIsNone(goal.get("category_name"))