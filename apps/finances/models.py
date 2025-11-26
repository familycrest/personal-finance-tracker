# # finances/models.py
from django.db import models
from django.core.exceptions import ValidationError
from base.settings import AUTH_USER_MODEL
from datetime import date


# Entry types enum
class EntryType(models.TextChoices):
    INCOME = "INCOME", "Income"
    EXPENSE = "EXPENSE", "Expense"


# Category model
class Category(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )

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
        max_length=10, choices=EntryType.choices, default=EntryType.EXPENSE
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
    def balance(self):
        pass

    @property
    def progress(self):
        """Calculate progress as percentage of goal amount based on entries."""
        if self.amount == 0:
            return None

        percentage = abs((self.balance / self.amount) * 100)
        return round(percentage, 2)


class ScanGoal:
    """This is only used to represent the bare minimum of a goal for the purposes of scanning."""

    name: str
    is_expense: bool
    amount: float
    corrected_bal: float
    exceeded: bool

    def __init__(
        self,
        name: str,
        is_expense: bool,
        amount: float,
        corrected_bal: float,
        exceeded: bool,
    ):
        self.name = name
        self.is_expense = is_expense
        self.amount = amount
        self.corrected_bal = corrected_bal
        self.exceeded = exceeded


class AccountGoal(Goal):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Account_Goals"
        verbose_name = "Account Goal"
        verbose_name_plural = "Account Goals"
        unique_together = ["user", "entry_type", "start_date", "end_date"]

    @property
    def balance(self):
        # Sum all entries for this category within the date range
        return self.user.get_balance(start_date=self.start_date, end_date=self.end_date)


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
    def balance(self):
        # Sum all entries for this category within the date range
        entries = Entry.objects.filter(
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date,
        )

        if len(entries) == 1:
            single = entries.first()
            return single.amount * (-1 if single.entry_type == "EXPENSE" else 1)
        else:
            income = (
                entries.filter(entry_type=EntryType.INCOME).aggregate(
                    total=models.Sum("amount")
                )["total"]
                or 0
            )
            expense = (
                entries.filter(entry_type=EntryType.EXPENSE).aggregate(
                    total=models.Sum("amount")
                )["total"]
                or 0
            )

        return income - expense

    # return the category goal by name
    def __str__(self):
        if not self.category:
            return self.name
        return f"{self.name} ({self.category.name})"
