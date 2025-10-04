# # finances/models.py
from django.db import models
from apps.accounts.models import UserAccount


# Entry types enum
class EntryType(models.TextChoices):
    INCOME = "INCOME", "Income"
    EXPENSE = "EXPENSE", "Expense"

# Category model
class Category(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )

    class Meta:
        db_table = "Categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ['user', 'name']

    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_entry_type(self):
        return self.entry_type
    
    def get_entries(self):
        return self.entry_set.all()
    
    def add_entry(self, name: str, description: str, entry_type: EntryType, date: str, amount: float):
        entry = Entry(
            user=self.user,
            category=self,
            name=name,
            description=description,
            entry_type=entry_type,
            date=date,
            amount=amount
        )
        entry.save()
        return entry
    
    def remove_entry(self, name: str):
        try:
            entry = self.entry_set.get(name=name)
            entry.delete()
            return True
        except Entry.DoesNotExist:
            return False
    
    def get_goals(self):
        return self.categorygoal_set.all()

    def add_goal(self, name: str, description: str, entry_type: EntryType, start_date: str, end_date: str, amount: float):
        goal = CategoryGoal(
            category=self,
            name=name,
            description=description,
            entry_type=entry_type,
            start_date=start_date,
            end_date=end_date,
            amount=amount
        )
        goal.save()
        return goal

    def remove_goal(self, name: str):
        try:
            goal = self.categorygoal_set.get(name=name)
            goal.delete()
            return True
        except CategoryGoal.DoesNotExist:
            return False

    def get_total(self):
        entries = self.get_entries()
        total = sum(entry.amount for entry in entries if entry.entry_type == self.entry_type)
        return total

    def get_goal_percentage(self):
        goals = self.get_goals()
        if not goals:
            return {} # No goals set
        
        goal_percentages = {}
        
        for goal in goals:
            total_entries_amount = self.get_total()
            total_goal_amount = goal.amount
            if total_goal_amount == 0:
                goal_percentages[goal] = 0.0
            else:
                percentage = float((total_entries_amount / total_goal_amount) * 100)
                goal_percentages[goal] = min(percentage, 100.0)  # Cap at 100%
        
        return goal_percentages

    def __str__(self):
        return self.name
    
# example
# goals: 
#     - expenses: -50
#     - income: 100, 200, 500
# entries:
#     - total_expenses: -40 (1/1 of expense goals)
#     - total_income: 150 (1/3 of income goals)

# goal_percentage = {
#     "expense -50": (40/50)*100 = 80%
#     "income 100": (150/100)*100 = 150% = 100%
#     "income 200": (150/200)*100 = 75%
#     "income 500": (150/500)*100 = 30%
# }

# Entry model
class Entry(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        db_table = "Entries"
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        unique_together = ["user", "category", "name"]
        
    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_entry_type(self):
        return self.entry_type
    
    def get_date(self):
        return self.date
    
    def get_amount(self):
        return self.amount

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

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

    @property
    def progress(self):
        # Placeholder logic - to be implemented based on goal type
        return 0

class AccountGoal(Goal):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = "Account_Goals"
        verbose_name = "Account Goal"
        verbose_name_plural = "Account Goals"
        unique_together = ["user", "name"]


class CategoryGoal(Goal):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "Category_Goals"
        verbose_name = "Category Goal"
        verbose_name_plural = "Category Goals"
        unique_together = ["category", "name"]
