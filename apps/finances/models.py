# # finances/models.py
from django.db import models
from apps.accounts.models import UserAccount
from decimal import Decimal


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
    # This goal is a placeholder and is NOT TO BE USED ANYWHERE ELSE.
    goal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) 

    class Meta:
        db_table = "Categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_entry_type(self):
        return self.entry_type

    def get_entries(self):
        return self.entry_set.all()

    def add_entry(
        self,
        name: str,
        description: str,
        entry_type: EntryType,
        date: str,
        amount: Decimal,
    ):
        try:
            # TODO: Add input checking here
            entry = Entry(
                user=self.user,
                category=self,
                name=name,
                description=description,
                entry_type=entry_type,
                date=date,
                amount=amount,
            )
            entry.save()
            return entry
        except Exception:
            return None

    def remove_entry(self, name: str):
        try:
            entry = self.entry_set.get(name=name)
            entry.delete()
            return True
        except Entry.DoesNotExist:
            return False

    def get_goals(self):
        return self.categorygoal_set.all()

    def add_goal(
        self,
        name: str,
        description: str,
        entry_type: EntryType,
        start_date: str,
        end_date: str,
        amount: Decimal,
    ):
        try:
            # TODO: Add input checking here
            goal = CategoryGoal(
                category=self,
                name=name,
                description=description,
                entry_type=entry_type,
                start_date=start_date,
                end_date=end_date,
                amount=amount,
            )
            goal.save()
            return goal
        except Exception:
            return None

    def remove_goal(self, name: str):
        try:
            goal = self.categorygoal_set.get(name=name)
            goal.delete()
            return True
        except CategoryGoal.DoesNotExist:
            return False

    def get_total(self):
        entries = self.get_entries()
        total = sum(
            (entry.amount for entry in entries if entry.entry_type == self.entry_type),
            Decimal("0"),
        )
        return total

    def get_goal_percentages(self):
        goals = self.get_goals()
        if not goals:
            return {}  # No goals set

        goal_percentages = {}

        for goal in goals:
            total_entries_amount = self.get_total()
            total_goal_amount = goal.amount
            if total_goal_amount == 0:
                goal_percentages[goal] = Decimal("0")
            else:
                percentage = (total_entries_amount / total_goal_amount) * Decimal("100")
                goal_percentages[goal] = percentage

        return goal_percentages


# Entry model
class Entry(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )
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

""" 
class Report {
    - title: String
    - message: String
    - creation_date: Date
    - graphs: List~BarGraph~

    + Report(title: String, message: String, creation_date: Date)
    + get_title() String
    + get_message() String
    + get_creation_date() Date
    + get_graphs() List~BarGraph~
}

class Analytics {
    - user_account: UserAccount
    - creation_date: Date
    - reports: List~Report~

    + Analytics(user_account: UserAccount, creation_date: Date)
    + get_user_account() UserAccount
    + get_creation_date() Date
    + get_reports() List~Report~
    + generate_account_report(start_date: Date, end_date: Date) Report
    + generate_category_report(category: Category, start_date: Date, end_date: Date) Report
    + check_goal_progress() List~Notification~
"""

class Report(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    creation_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
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
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    reports = models.ManyToManyField(Report, blank=True)

    class Meta:
        db_table = "Analytics"
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"

    def get_user_account(self):
        return self.user_account

    def get_creation_date(self):
        return self.creation_date

    def get_reports(self):
        return self.reports.all()

    def generate_account_report(self, start_date=None, end_date=None):
        if start_date is None or end_date is None:
            message = "All time account report"
        else:
            message = f"Account report from {start_date} to {end_date}"

        total_income = sum(
            entry.amount for entry in Entry.objects.filter(user=self.user_account, entry_type=EntryType.INCOME)
        )
        total_expenses = sum(
            entry.amount for entry in Entry.objects.filter(user=self.user_account, entry_type=EntryType.EXPENSE)
        )
        net_savings = total_income - total_expenses 


        graph_data = [
            {
                "type": "bar",
                "title": "My Expenses",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [500, 700, 300, 400],
                },
                "options": {
                    "color": "red",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "bar",
                "title": "My Incomes",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [1500, 1700, 1300, 1400],
                },
                "options": {
                    "color": "green",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "bar",
                "title": "Expenses vs Incomes",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "expenses": [500, 700, 300, 400],
                    "incomes": [1500, 1700, 1300, 1400],
                },
                "options": {
                    "colors": ["red", "green"],
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "pie",
                "title": "Expense Distribution",
                "data": {
                    "labels": ["Rent", "Food", "Transport", "Entertainment"],
                    "values": [40, 30, 20, 10],
                },
                "options": {
                    "colors": ["blue", "orange", "grey", "purple"],
                },
            },
            {
                "type": "pie",
                "title": "Income Distribution",
                "data": {
                    "labels": ["Salary", "Freelance", "Investments"],
                    "values": [70, 20, 10],
                },
                "options": {
                    "colors": ["green", "lightgreen", "darkgreen"],
                },
            },
            {
                "type": "line",
                "title": "Net Savings Over Time",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [1000, 1000, 1000, 1000],
                },
                "options": {
                    "color": "blue",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "line",
                "title": "Spending Trends",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [500, 700, 300, 400],
                },
                "options": {
                    "color": "red",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "line",
                "title": "Income Trends",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [1500, 1700, 1300, 1400],
                },
                "options": {
                    "color": "green",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "table",
                "title": "Account Summary",
                "data": {
                    "headers": ["Type", "Total"],
                    "rows": [
                        ["Total Income", f"${total_income}"],
                        ["Total Expenses", f"${total_expenses}"],
                        ["Net Savings", f"${net_savings}"],
                    ],
                },
                "options": {
                    "column_alignments": ["left", "right"],
                },
            },
            {
                "type": "table",
                "title": "Monthly Summary",
                "data": {
                    "headers": ["Month", "Income", "Expenses", "Net Savings"],
                    "rows": [
                        ["January", 1500, 500, 1000],
                        ["February", 1700, 700, 1000],
                        ["March", 1300, 300, 1000],
                        ["April", 1400, 400, 1000],
                    ],
                },
                "options": {
                    "column_alignments": ["left", "right", "right", "right"],
                },
            }
        ]
        
        report = Report(
            title="Account Report",
            message=message,
            start_date=start_date,
            end_date=end_date,
            graphs=graph_data,           
        )
        report.save()
        self.reports.add(report)
        return report

    def generate_category_report(self, category, start_date=None, end_date=None):
        if start_date is None or end_date is None:
            message = f"All time report for {category.name}"
        else:
            message = f"Report for {category.name} from {start_date} to {end_date}"
        graph_data = [
            {  
                "type": "bar",
                "title": f"{category.name} - Monthly {category.entry_type.capitalize()}",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [200, 300, 150, 250],
                },
                "options": {
                    "color": "blue" if category.entry_type == EntryType.INCOME else "red",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "pie",
                "title": f"{category.name} - {category.entry_type.capitalize()} Distribution",
                "data": {
                    "labels": ["Subcategory 1", "Subcategory 2", "Subcategory 3"],
                    "values": [50, 30, 20],
                },
                "options": {
                    "colors": ["blue", "orange", "grey"] if category.entry_type == EntryType.INCOME else ["red", "pink", "purple"],
                },
            },
            {
                "type": "line",
                "title": f"{category.name} - {category.entry_type.capitalize()} Trends",
                "data": {
                    "labels": ["January", "February", "March", "April"],
                    "values": [200, 300, 150, 250],
                },
                "options": {
                    "color": "blue" if category.entry_type == EntryType.INCOME else "red",
                    "x_label": "Months",
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "table",
                "title": f"{category.name} - {category.entry_type.capitalize()} Summary",
                "data": {
                    "headers": ["Month", category.entry_type.capitalize()],
                    "rows": [
                        ["January", 200],
                        ["February", 300],
                        ["March", 150],
                        ["April", 250],
                    ],
                },
                "options": {
                    "column_alignments": ["left", "right"],
                },
            }  
        ]
        report = Report(
            title=f"Category Report: {category.name}",
            message=message,
            start_date=start_date,
            end_date=end_date,
            graphs=graph_data,
        )
        report.save()
        self.reports.add(report)
        return report

    def check_goal_progress(self):
        goal_progress = []
        categories = Category.objects.filter(user=self.user_account)
        for category in categories:
            goal_percentages = category.get_goal_percentages()
            for goal in goal_percentages:
                percentage = goal_percentages[goal]
                if percentage >= 100:
                    goal_progress.append(
                        f"Goal '{goal.name}' for category '{category.name}' has been achieved!"
                    )
                elif percentage >= 75:
                    goal_progress.append(
                        f"Goal '{goal.name}' for category '{category.name}' is at {percentage:.2f}% completion."
                    )
               
        return goal_progress 
