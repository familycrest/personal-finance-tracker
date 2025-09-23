# personal_finance_tracker_app/models.py
from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    # include a dropdown for user to choose category of expense.
    CATEGORY_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    # include a dropdown menu to ask the user if they stayed within their goals
    GOALS_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # each transaction belongs to a user
    date = models.DateField()
    transaction = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    reports = models.CharField(max_length=255, blank=True, null=True)
    goals = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction} ({self.category}) - {self.date}"
