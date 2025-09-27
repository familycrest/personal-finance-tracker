from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class UserAccount(AbstractUser):
    # AbstractUser already includes username, email, first_name, last_name, password, etc.
    def __str__(self):
        return self.username

# Entry types enum (shared between category and Entry)
class EntryType(models.TextChoices):
    INCOME = "INCOME", "Income"
    EXPENSE = "EXPENSE", "Expense"

# Category model
class Category(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )

    class Meta:
        verbose_name_plural = "Categories"  

    def __str__(self):
        return self.name

# Entry model
class Entry(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    entry_type = models.CharField(
        max_length=10, 
        choices=EntryType.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


    class Meta:
        verbose_name_plural = "Entries"


    def __str__(self):
        return f"{self.name} - {self.amount}"

# Goal model
class Goal(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    entry_type = models.CharField(max_length=10,choices=EntryType.choices)
    start_date = models.DateField()
    end_date = models.DateField()                           
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Goals"

    def __str__(self):
        return self.name
    
    @property
    def progress(self):
        # Placeholder logic - to be implemented based on goal type
        return 0
    
# Specific goal types (subclasses of Goal)
class CategoryBudgetGoal(Goal):
    pass

class CategoryIncomeGoal(Goal):
    pass

class AccountBudgetGoal(Goal):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

class AccountIncomeGoal(Goal):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
 
# Notification type enum
class NotificationType(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    ALERT = "ALERT", "Alert"

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=10, 
        choices=NotificationType.choices,
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.title} ({'Read' if self.is_read else 'Unread'})"
