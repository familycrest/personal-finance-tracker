# # finances/models.py
from django.db import models
from django.core.exceptions import ValidationError
from base.settings import AUTH_USER_MODEL
from decimal import Decimal
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
        # Placeholder logic - to be implemented based on goal type
        return 0


class AccountGoal(Goal):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Account_Goals"
        verbose_name = "Account Goal"
        verbose_name_plural = "Account Goals"
        unique_together = ["user", "entry_type", "start_date", "end_date"]


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

    # return the category goal by name
    def __str__(self):
        return f"{self.name} ({self.category.name})"
