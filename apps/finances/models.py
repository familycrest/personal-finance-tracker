# # finances/models.py
from django.db import models
from django.core.exceptions import ValidationError
from base.settings import AUTH_USER_MODEL
from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta



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
    user_account = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    reports = models.ManyToManyField(Report, blank=True)

    class Meta:
        db_table = "Analytics"
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"


    def generate_account_report(self, period, interval):
        blocks = []
        category_totals_expenses = {}
        category_totals_income = {}

        if period == "week":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(weeks=1)
            for i in range(8):
                day = start_date + timedelta(days=i)
                block_start = day
                block_end = day
                blocks.append((block_start, block_end))
        
        elif period == "month":
            end_date = datetime.now().date()
            if interval == "day":
                start_date = end_date - timedelta(days=30)
                for i in range(31):
                    day = start_date + timedelta(days=i)
                    block_start = day
                    block_end = day
                    blocks.append((block_start, block_end))

            else:  # interval == "week"
                four_weeks_ago = end_date - relativedelta(weeks=4)
                start_date = four_weeks_ago - timedelta(days=four_weeks_ago.weekday())
                current = start_date
                while current <= end_date:
                    block_start = current
                    block_end = current + timedelta(days=6)
                    if block_end > end_date:
                        block_end = end_date
                    blocks.append((block_start, block_end))
                    current += timedelta(weeks=1)

        elif period == "year":
            end_date = datetime.now().date()
            if interval == "day":
                start_date = end_date - timedelta(days=365)
                for i in range(366):
                    day = start_date + timedelta(days=i)
                    block_start = day
                    block_end = day
                    blocks.append((block_start, block_end))

            elif interval == "week":
                four_weeks_ago = end_date - relativedelta(weeks=52)
                start_date = four_weeks_ago - timedelta(days=four_weeks_ago.weekday())
                current = start_date
                while current <= end_date:
                    block_start = current
                    block_end = current + timedelta(days=6)
                    if block_end > end_date:
                        block_end = end_date
                    blocks.append((block_start, block_end))
                    current += timedelta(weeks=1)

            else:  # interval == "month"
                start_date = (end_date - relativedelta(months=12)).replace(day=1)
                current = start_date
                while current <= end_date:
                    block_start = current
                    next_month = current + relativedelta(months=1)
                    block_end = next_month - timedelta(days=1)
                    if block_end > end_date:
                        block_end = end_date
                    blocks.append((block_start, block_end))
                    current = next_month

        title_income = f"{period.capitalize()}ly Income by {interval.capitalize()}"
        title_expenses = f"{period.capitalize()}ly Expenses by {interval.capitalize()}"

        grouped_income = []
        grouped_expenses = []
        for block_start, block_end in blocks:
            block_income = sum(
                entry.amount for entry in Entry.objects.filter(
                    user=self.user_account,
                    entry_type=EntryType.INCOME,
                    date__range=(block_start, block_end)
                )
            )
            block_expenses = sum(
                entry.amount for entry in Entry.objects.filter(
                    user=self.user_account,
                    entry_type=EntryType.EXPENSE,
                    date__range=(block_start, block_end)
                )
            )
            grouped_income.append(float(block_income))
            grouped_expenses.append(float(block_expenses))

        labels = []
        for block_start, block_end in blocks:
            if interval == "day":
                labels.append(block_start.strftime("%Y-%m-%d"))
            elif interval == "week":
                labels.append(f"M {block_start.strftime('%m-%d')}")
            else:  # interval == "month"
                labels.append(block_start.strftime("%b %Y"))

        graph_data = [
            {
                "type": "bar",
                "title": title_expenses,
                "data": {           
                    "labels": labels,
                    "values": grouped_expenses,
                },
                "options": {
                    "color": "red",
                    "x_label": interval.capitalize(),
                    "y_label": "Amount ($)",
                },
            },
            {
                "type": "bar",
                "title": title_income,
                "data": {
                    "labels": labels,
                    "values": grouped_income,
                },
                "options": {
                    "color": "green",
                    "x_label": interval.capitalize(),
                    "y_label": "Amount ($)",
                },
            },
        ]

        print(graph_data)
        print(title_income)
        print(title_expenses)

        
        report = Report(
            title="Account Report",
            message=f"View your income and expenses over the selected period and interval.",
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