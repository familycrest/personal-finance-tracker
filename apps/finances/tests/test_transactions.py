# finances/tests/test_transactions.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Category, Entry, EntryType
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

# 1. perform testing on the models
class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

    # create a test category to use
    def test_create_category(self):
        category = Category.objects.create(
            user=self.user,
            name="Food",
            entry_type=EntryType.EXPENSE,
            description="Expenses for food"
        )
        self.assertEqual(str(category), "Food")
        self.assertEqual(category.entry_type, EntryType.EXPENSE)

    def test_unique_category_name_per_user(self):
        Category.objects.create(
            user=self.user,
            name="Transport",
            entry_type=EntryType.EXPENSE
        )
        with self.assertRaises(Exception):
            Category.objects.create(
                user=self.user,
                name="Transport",
                entry_type=EntryType.EXPENSE
            )

class EntryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category_income = Category.objects.create(
            user=self.user,
            name="Salary",
            entry_type=EntryType.INCOME
        )
        self.category_expense = Category.objects.create(
            user=self.user,
            name="Food",
            entry_type=EntryType.EXPENSE
        )

    def test_create_income_entry(self):
        entry = Entry.objects.create(
            user=self.user,
            category=self.category_income,
            name="November Salary",
            entry_type=EntryType.INCOME,
            amount=5000,
            date=date.today()
        )
        self.assertEqual(str(entry), f"November Salary - {entry.amount}")
        self.assertEqual(entry.entry_type, EntryType.INCOME)

    def test_create_expense_entry(self):
        entry = Entry.objects.create(
            user=self.user,
            category=self.category_expense,
            name="Groceries",
            entry_type=EntryType.EXPENSE,
            amount=150,
            date=date.today()
        )
        self.assertEqual(str(entry), f"Groceries - {entry.amount}")
        self.assertEqual(entry.entry_type, EntryType.EXPENSE)

    def test_entry_category_type_mismatch_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            Entry.objects.create(
                user=self.user,
                category=self.category_income,
                name="Mismatch Test",
                entry_type=EntryType.EXPENSE,
                amount=100,
                date=date.today()
            )

# 2. perform testing for the transactions view
class TransactionsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.client.login(username="testuser", password="password")
        self.category = Category.objects.create(
            user=self.user, name="Food", entry_type=EntryType.EXPENSE
        )

        self.url = reverse("transactions")

    # GET the tests for transaction views
    def test_transactions_page_loads(self):
        # should return 200 if correct
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finances/transactions.html")

    def test_transactions_lists_user_entries(self):
        # get entries from the logged in user
        entry = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Groceries",
            entry_type=EntryType.EXPENSE,
            amount=50,
            date=timezone.localdate(),
        )

        response = self.client.get(self.url)
        entries_output = response.context["entries_output"]

        self.assertIn(entry, entries_output)

    def test_edit_mode_loads_correct_entry(self):
        # test to make sure the edit feature works
        entry = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Lunch",
            entry_type=EntryType.EXPENSE,
            amount=20,
            date=timezone.localdate()
        )

        response = self.client.get(self.url, {"edit": entry.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["edit_id"], entry.id)
        self.assertEqual(response.context["entry_form"].instance, entry)

    def test_cannot_edit_other_users_entry(self):
        other_user = User.objects.create_user(
            username="guestuser", password="password"
        )

        other_category = Category.objects.create(
            user=other_user,
            name="Other Salary",
            entry_type=EntryType.INCOME
        )

        entry_other = Entry.objects.create(
            user=other_user,
            category=other_category,
            name="Hidden Entry",
            entry_type=EntryType.INCOME,
            amount=999,
            date=timezone.localdate(),
        )

        # when editing, the page should redirect back to transactions url
        response = self.client.get(self.url, {"edit": entry_other.id})
        self.assertEqual(response.status_code, 302)

    # POST testing for transactions views
    def test_add_new_entry_via_post(self):
        # test to make sure a new entry is created when posting
        data = {
            "name": "New Expense",
            "entry_type": EntryType.EXPENSE,
            "amount": 100,
            "category": self.category.id,
            "date": timezone.localdate(),
        }

        response = self.client.post(self.url, data)
        # verify a 302 code after saving
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Entry.objects.count(), 1)

        entry = Entry.objects.first()
        self.assertEqual(entry.name, "New Expense")
        self.assertEqual(entry.amount, 100)

    def test_edit_existing_entry(self):
        # test that POST create
        entry = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Old name",
            entry_type=EntryType.EXPENSE,
            amount=10,
            date=timezone.localdate(),
        )

        data = {
            "name": "Updated Name",
            "entry_type": EntryType.EXPENSE,
            "amount": 20,
            "category": self.category.id,
            "date": timezone.localdate(),
        }

        response = self.client.post(f"{self.url}?edit={entry.id}", data)

        self.assertEqual(response.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.name, "Updated Name")
        self.assertEqual(entry.amount, 20)

    def test_cannot_edit_other_users_entry_post(self):
        # test for POST entries not updating other user's entries
        other_user = User.objects.create_user(
            username="guestuser", password="password"
        )

        other_category = Category.objects.create(
            user=other_user,
            name="Other Expense",
            entry_type=EntryType.EXPENSE
        )

        entry_other = Entry.objects.create(
            user=other_user,
            category=other_category,
            name="Other Person",
            entry_type=EntryType.EXPENSE,
            amount=70,
            date=timezone.localdate(),
        )

        data = {
            "name": "Hack Attempt",
            "entry_type": EntryType.EXPENSE,
            "amount": 999,
            "category": self.category.id,
            "date": timezone.localdate(),
        }

        response = self.client.post(f"{self.url}?edit={entry_other.id}", data)

        # test for redirection with a 302 code
        self.assertEqual(response.status_code, 302)
        entry_other.refresh_from_db()
        self.assertEqual(entry_other.name, "Other Person")
        self.assertEqual(entry_other.amount, 70)

# 3. perform testing on the  transactions filter
class EntryFilterFormTests(TestCase):
    def setUp(self):
        # create a user and a guest user
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        other_user = User.objects.create_user(
            username="guestuser", password="password"
        )

        # provide test categories
        self.category1 = Category.objects.create(
            user=self.user, name="Food", entry_type=EntryType.EXPENSE
        )
        self.category2 = Category.objects.create(
            user=self.user, name="Shopping", entry_type=EntryType.EXPENSE
        )
        self.other_category = Category.objects.create(
            user=self.other_user, name="Salary", entry_type=EntryType.INCOME
        )

        # provide test entries
        self.entry_old = Entry.objects.create(
            user=self.user,
            category=self.category1,
            name="Groceries",
            entry_type=EntryType.EXPENSE,
            amount=140,
            # use a time difference of 10 days for testing
            date=timezone.localdate() - timedelta(days=10),
        )
        self.entry_recent = Entry.objects.create(
            user=self.user,
            category=self.category2,
            name="Black Friday Sales",
            entry_type=EntryType.EXPENSE,
            amount=100,
            date=timezone.localdate(),
        )

    # test for valid inputs into form
    def test_valid_filter(self):
        form = EntryFilterForm({
            "category": self.category1.id,
            # create a custom time frame
            "date_start": timezone.localdate() - timedelta(days=20),
            "date_end": timezone.localdate(),
        }, user=self.user)

        self.assertTrue(form.is_valid())

    # test for invalid date ranges
    def test_invalid_date_range(self):
        form = EntryFilterForm({
            "category": self.category1.id,
            # create a custom time frame
            "date_start": timezone.localdate(),
            "date_end": timezone.localdate() - timedelta(days=5),
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("date_end", form.errors)

    # test for missinf optional fields
    def test_optional_fields(self):
        # leave the form empty to test
        form = EntryFilterForm({}, user=self.user)
        self.assertTrue(form.is_valid())

    # test for funtional categories filtering
    def test_category_dropdown_accuracy(self):
        form = EntryFilterForm()
        user_categories = form.fields["category"].queryset

        self.assertIn(self.category1, user_categories)
        self.assertIn(self.category2, user_categories)
        self.assertNotIn(self.other_category, user_categories)

    # test to verify entries are filtered by date
    def test_filter_entries_by_date(self):
        form = EntryFilterForm({
            "date_start": timezone.localdate() - timedelta(days=5),
            "date_end": timezone.localdate() + timedelta(days=1),
        }, user=self.user)
        self.assertTrue(form.is_valid())

        # test applying the filter
        cleaned = form.cleaned_data
        qs = Entry.objects.filter(user=self.user)

        # only keep entries on or after the start date
        if cleaned["date_start"]:
            qs = qs.filter(date__gte=cleaned["date_start"])

        # only keep entries on or before the end date
        if cleaned["date_end"]:
            qs = qs.filter(date__lte=cleaned["date_end"])

        self.assertIn(self.entry_recent, qs)
        self.assertNotIn(self.entry_old, qs)


# 4. perform testing on the delete transactions url
class DeleteTransactionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.other_user = User.objects.create_user(username="guestUser", password="password")

        # create categories for each user
        self.category = Category.objects.create(
            user=self.user, name="Shopping", entry_type=EntryType.EXPENSE
        )
        self.other_category = Category.objects.create(
            user=self.other_user, name="Salary", entry_type=EntryType.INCOME
        )

        # create the entry
        self.user_entry = Entry.objects.create(
            user=self.user,
            category=self.category,
            name="Labubus",
            entry_type=EntryType.EXPENSE,
            amount=80,
            date=timezone.localdate(),
        )
        self.other_entry = Entry.objects.create(
            user=self.other_user,
            category=self.other_category,
            name="Large Paycheck",
            entry_type=EntryType.INCOME,
            amount=8000,
            date=timezone.localdate(),
        )

        # login as testuser
        self.client.login(username="testuser", password="password")

    def test_delete_own_entry(self):
        # test if user can delete their own entries
        url = reverse("delete_transactions", args=[self.user_entry.id])
        response = self.client.post(url)

        # test fot redirection after deletion
        self.assertEqual(response.status_code, 302)
        # verify the entry is really deleted
        self.assertFalse(Entry.objects.filter(id=self.user_entry.id).exists())

    def test_cannot_delete_other_users_entry(self):
        # test if user can delete other user's entries. Should not be able to!
        url = reverse("delete_transactions", args=[self.other_entry.id])
        response = self.client.post(url)

        # test for redirection after error deletion
        self.assertIn(response.status_code, 302)

        # verify the entry is not deleted
        self.assertTrue(Entry.objects.filter(id=self.other_entry.id).exists())

