from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class Account(AbstractUser):
    # AbstracUser already includes username, email, first_name, last_name, password, etc.
    def __str__(self):
        return self.username


# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    entry_type = models.CharField(
        max_length=10, choices=[("INCOME", "Income"), ("EXPENSE", "Expense")]
    )

    class Meta:
        verbose_name_plural = "Categories"  

    def __str__(self):
        return self.name

# Entry model
class Entry(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    entry_type = models.CharField(
        max_length=10, choices=[("INCOME", "Income"), ("EXPENSE", "Expense")]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


    class Meta:
        verbose_name_plural = "Entries"


    def __str__(self):
        return f"{self.name} - {self.amount}"

# Goal model
class Goal(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    class Meta:
        verbose_name_plural = "Goals"

def __str__(self):
    return f"{self.name} - Target: {self.target_amount}"

# Notification model
class Notification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=10, choices=[("EMAIL", "Email"), ("ALERT", "Alert")]
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


def __str__(self):
    return f"{self.title} ({'Read' if self.is_read else 'Unread'})"
