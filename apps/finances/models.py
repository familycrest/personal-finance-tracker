# # finances/models.py
from django.db import models
from django.core.exceptions import ValidationError
from base.settings import AUTH_USER_MODEL
from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date



# Entry types enum  
class EntryType(models.TextChoices):
    INCOME = "INCOME", "Income"
    EXPENSE = "EXPENSE", "Expense"

# Category model
class Category(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )
    # This goal is a placeholder and is NOT TO BE USED ANYWHERE ELSE.
    # goal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        db_table = "Categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name


# Entry model
class Entry(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
        default=EntryType.EXPENSE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        db_table = "Entries"
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        unique_together = ["user", "category", "name"]

    def clean(self):
        super().clean()
        # If entry has a category, entry_type must match category's entry_type
        if self.category and self.entry_type != self.category.entry_type:
            raise ValidationError(
                f"Entry type must be {self.category.entry_type} to match the category '{self.category.name}'."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.amount}"


# Goal model
class Goal(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # switched the order
    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    
    def is_current(self) -> bool:
        today = date.today()
        if (self.start_date > today) or (self.end_date < today):
            return False
        else:
            return True

    @property
    def progress(self):
        # Placeholder logic - to be implemented in subclasses
        return None


class AccountGoal(Goal):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Account_Goals"
        verbose_name = "Account Goal"
        verbose_name_plural = "Account Goals"
        unique_together = ["user", "entry_type", "start_date", "end_date"]

    @property
    def progress(self):
        """Calculate progress as percentage of goal amount based on entries."""
        if self.amount == 0:
            return None

        # Sum all entries of matching type for this user within the date range
        entries = Entry.objects.filter(
            user=self.user,
            entry_type=self.entry_type,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        total = sum(entry.amount for entry in entries)

        percentage = (total / self.amount) * 100
        return round(percentage, 2)


class CategoryGoal(Goal):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "Category_Goals"
        verbose_name = "Category Goal"
        verbose_name_plural = "Category Goals"
        unique_together = ["category", "start_date", "end_date"]

    def save(self, *args, **kwargs):
        # Auto-set entry_type from category to ensure consistency
        if self.category:
            self.entry_type = self.category.entry_type
        super().save(*args, **kwargs)

    @property
    def progress(self):
        """Calculate progress as percentage of goal amount based on category entries."""
        if self.amount == 0:
            return None

        # Sum all entries for this category within the date range
        entries = Entry.objects.filter(
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        total = sum(entry.amount for entry in entries)

        percentage = (total / self.amount) * 100
        return round(percentage, 2)

    # return the category goal by name
    def __str__(self):
        return f"{self.name} ({self.category.name})"

class Report(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    graphs = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "Reports"
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message

    def get_creation_date(self):
        return self.creation_date

    def get_graphs(self):
        return self.graphs

class Analytics(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    reports = models.ManyToManyField(Report, blank=True)

    class Meta:
        db_table = "Analytics"
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"


    def generate_account_report(self, start_date: date, end_date: date):
        # Add one to account for the start date and end date being included
        TIME_LENGTH = (end_date - start_date).days + 1
        # Create a dictionary of all days in the time period requested with an inner dictionary of summed expenses and incomes
        day_data = {(end_date -  timedelta(days=i)): {EntryType.EXPENSE: Decimal("0"), EntryType.INCOME: Decimal("0")} for i in range(TIME_LENGTH)}
        transactions = Entry.objects.filter(user=self.user, date__gte=start_date, date__lte=end_date)
        
        # Populate the dictionary with the sums of all transactions for the date range
        for transaction in transactions:
            date = transaction.date
            entry_type = transaction.entry_type
            amount = transaction.amount
            day_data[date][entry_type] += amount

        return day_data


    def generate_category_report(self, category: Category, start_date: date, end_date: date):
        # Add one to account for the start date and end date being included
        TIME_LENGTH = (end_date - start_date).days + 1
        # Create a dictionary of all days in the time period requested with the value representing the sum of transactions of the category's type
        day_data = {(end_date - timedelta(days=i)): Decimal("0") for i in range(TIME_LENGTH)}
        transactions = Entry.objects.filter(user=self.user, date__gte=start_date, date__lte=end_date)

        # Populate the dictionary with the sums of all of the category's transactions for the date range
        for transaction in transactions:
            date = transaction.date
            amount = transaction.amount
            day_data[date] += amount

        return day_data


    def check_account_goal_progress(self):
        goal_progress = {}
        goals = AccountGoal.objects.filter(user=self.user_account)
        for goal in goals:
            total_entries_amount = sum(
                entry.amount for entry in Entry.objects.filter(
                    user=self.user_account,
                    entry_type=goal.entry_type
                )
            )
            total_goal_amount = goal.amount
            if total_goal_amount == 0:
                percentage = 0
            else:
                percentage = (total_entries_amount / total_goal_amount) * 100

            if percentage >= 100:
                goal_progress[goal.id] = 100.0  
            else:
                goal_progress[goal.id] = float(round(percentage, 2))

        return goal_progress

    def check_category_goal_progress(self):
        goal_progress = {}
        categories = Category.objects.filter(user=self.user_account)
        for category in categories:
            goal_percentages = category.get_goal_percentages()
            category_goal_progress = {}
            for goal, goal_percentage in goal_percentages.items():
                if goal_percentage >= 100:
                    category_goal_progress[goal.id] = 100.0  
                else:
                    category_goal_progress[goal.id] = float(round(goal_percentage, 2))
            goal_progress[category.id] = category_goal_progress  

        return goal_progress 