from datetime import date, timedelta
from calendar import monthrange
from django.utils import timezone
from django import forms

from .models import Category, Entry, Goal, AccountGoal, CategoryGoal


# Form for adding/editing categories
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "entry_type",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Category Name",
                    "class": "form-control",
                    "id": "category-name",
                }
            ),
            "entry_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "category-type",
                }
            ),
        }

    # Constructor to include user
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    # Clean field method to check if category name already exists
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            return name

        # Looks up categories with the same name (case-insensitive)
        query_set = Category.objects.filter(user=self.user, name__iexact=name)

        # If this is an edit form, don't compare against itself
        if self.instance.pk:
            query_set = query_set.exclude(pk=self.instance.pk)

        # Raise error if existing name found
        if query_set.exists():
            raise forms.ValidationError(f"You already have a category named '{name}'.")

        return name

    # Clean field method to prevent user from editing entry type for existing categories
    def clean_entry_type(self):
        entry_type = self.cleaned_data.get("entry_type")

        if self.instance and self.instance.pk:
            if entry_type != self.instance.entry_type:
                raise forms.ValidationError("You cannot change the entry_type of existing category.")
            return self.instance.entry_type

        return entry_type


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = [
            "date",
            "name",
            "amount",
            "entry_type",
            "category",
            "description",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "id": "transaction-date",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Transaction Name",
                    "class": "form-control",
                    "id": "transaction-name",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "$---.--",
                    "class": "form-control",
                    "id": "transaction-amount",
                    "min": 0,
                }
            ),
            "entry_type": forms.RadioSelect(
                attrs={
                    "label": "Transaction Type",
                    "class": "form-select",
                    "id": "transaction-type",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "transaction-category",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "placeholder": "Description",
                    "class": "form-control",
                    "id": "transaction-description",
                    "rows": 3,
                }
            ),
        }

    # Populates categories in the dropdown at runtime
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        entry_type = cleaned_data.get("entry_type")
        amount = cleaned_data.get("amount")
        date_val = cleaned_data.get("date")

        # If entry has a category, entry_type must match category's entry_type
        if category and entry_type and entry_type != category.entry_type:
            self.add_error(
                "entry_type",
                f"Entry type must be {category.entry_type} to match the category '{category.name}'.",
            )

        # add this to ensure positive numbers
        if amount is not None and amount < 0:
            self.add_error("amount", "The amount cannot be negative.")

        # make sure the date isn't in the future
        if date_val and date_val > timezone.localdate():
            self.add_error("date", "Date cannot be in the future.")

        return cleaned_data


class EntryFilterForm(forms.Form):
    date_start = forms.DateField(
        label="From",
        required=False,
        initial=None,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_end = forms.DateField(
        label="To",
        required=False,
        initial=None,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    name = forms.CharField(label="Transaction Name", required=False)
    amount = forms.IntegerField(
        label="Amount",
        required=False,
        initial=None,
        widget=forms.NumberInput(attrs={"placeholder": "$---.--"}),
        min_value=0,
    )
    entry_type_income = forms.BooleanField(
        label="Income Transactions",
        required=False,
        initial=True,
    )
    entry_type_expense = forms.BooleanField(
        label="Expense Transactions",
        required=False,
        initial=True,
    )
    category = forms.ChoiceField(
        required=False,
        initial=None,
    )

    # Populates categories in the filter at runtime
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "All Categories")]
        if user is not None:
            choices += list(
                Category.objects.filter(user=user)
                .order_by("name")
                .values_list("id", "name")
            )
        self.fields["category"].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start and date_end:
            if date_start > date_end:
                self.add_error(
                    "date_start",
                    "The start date must be earlier than the end date.",
                )

            if date_start > date.today():
                self.add_error("date_start", "The start date cannot be in the future.")

            if date_end > date.today():
                self.add_error("date_end", "The end date cannot be in the future.")

        return cleaned_data


class AccountReportFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ("week", "The Last Week"),
        ("month", "The Last Month"),
        ("year", "The Last Year"),
    ]
    INTERVAL_CHOICES = [
        ("day", "Day"),
        ("week", "Week"),
        ("month", "Month"),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        label="Period",
        initial="month",
    )
    interval = forms.ChoiceField(
        choices=INTERVAL_CHOICES,
        label="Interval",
        initial="week",
    )


class CategoryReportFilterForm(AccountReportFilterForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        label="Category",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user)


class PieReportFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ("week", "The Last Week"),
        ("month", "The Last Month"),
        ("year", "The Last Year"),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        label="Period",
        initial="month",
    )


class AddGoalForm(forms.ModelForm):
    """
    Base of AddAccountGoalForm and AddCategoryGoalForm; abstracts away some of the clean logic.
    Not meant to be used directly.
    """

    TIME_CHOICES = (
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    )
    time_length = forms.ChoiceField(choices=TIME_CHOICES, initial="monthly")

    class Meta:
        model = Goal
        fields = ["name", "description", "entry_type", "time_length", "amount"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        time_length = cleaned_data.get("time_length")
        today = date.today()

        # This logic and the forms should be changed to allow for recurring goals
        # If weekly goal, set the start date at the beginning of the week and the end date at the end of the week
        if time_length == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        # If monthly goal, set the start date at the beginning of the month and the end date at the end of the month
        elif time_length == "monthly":
            start_date = date(today.year, today.month, 1)
            last_day_of_month = monthrange(today.year, today.month)[1]
            end_date = date(today.year, today.month, last_day_of_month)
        # If yearly goal, set the start date at the beginning of the year and the end date at the end of the year
        elif time_length == "yearly":
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)
        else:
            # If time_length is invalid or not provided, don't set dates
            return cleaned_data

        cleaned_data["start_date"] = start_date
        cleaned_data["end_date"] = end_date

        return cleaned_data


class AddAccountGoalForm(AddGoalForm):
    """
    Form for adding an account goal. The clean function checks to make sure the user doesn't have any
    account goals with the same start date, end date, and transaction type of the goal to be added.
    """

    class Meta:
        model = AccountGoal
        fields = ["name", "description", "entry_type", "time_length", "amount"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if self.user:
            entry_type = cleaned_data.get("entry_type")
            if AccountGoal.objects.filter(
                user=self.user,
                entry_type=entry_type,
                start_date=start_date,
                end_date=end_date,
            ).exists():
                self.add_error(
                    "time_length",
                    f"You already have an {entry_type.capitalize()} goal for that time range.",
                )

        return cleaned_data

    def save(self, commit=True):
        goal = super().save(commit=False)

        goal.start_date = self.cleaned_data["start_date"]
        goal.end_date = self.cleaned_data["end_date"]
        goal.user = self.user

        if commit:
            goal.save()
        return goal


class EditAccountGoalForm(forms.ModelForm):
    class Meta:
        model = AccountGoal
        fields = ["name", "description", "amount"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class AddCategoryGoalForm(AddGoalForm):
    """
    Form for adding a category goal. The clean function checks to make sure the user doesn't have any
    category goals with the same category, start date, and end date.
    """

    class Meta:
        model = CategoryGoal
        fields = ["category", "name", "description", "time_length", "amount"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter category dropdown to only show user's categories
        if self.user:
            self.fields["category"].queryset = Category.objects.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Only check for duplicates if we have all required fields
        if self.user and start_date and end_date:
            category = cleaned_data.get("category")
            if category:
                if CategoryGoal.objects.filter(
                    category=category, start_date=start_date, end_date=end_date
                ).exists():
                    self.add_error(
                        "time_length",
                        "This category already has a goal for that time range.",
                    )

        return cleaned_data

    def save(self, commit=True):
        goal = super().save(commit=False)

        goal.start_date = self.cleaned_data["start_date"]
        goal.end_date = self.cleaned_data["end_date"]

        if commit:
            goal.save()
        return goal


class EditCategoryGoalForm(forms.ModelForm):
    class Meta:
        model = CategoryGoal
        fields = ["name", "description", "amount"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
