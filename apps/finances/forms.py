from datetime import datetime, timezone, date

from django import forms

from .models import Category, Entry, EntryType

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "entry_type"] #, "goal"] # removed goal. will need to rework it after category edits are merged
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
            "goal": forms.NumberInput(
                attrs={
                    "placeholder": "$---.--",
                    "class": "form-control",
                    "id": "category-goal",
                }
            ),
        }


# class EditCategoryForm(forms.ModelForm):
#     id = forms.IntegerField(widget=forms.HiddenInput())

#     class Meta:
#         model = Category
#         fields = ["id", "name", "entry_type", "goal"]
#         widgets = {
#             "name": forms.TextInput(attrs={"class": "form-control"}),
#             "entry_type": forms.Select(attrs={"class": "form-select"}),
#             "goal": forms.NumberInput(attrs={"class": "form-control"}),
#         }

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["date", "name", "amount", "entry_type", "category", "description"]
        
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
                    "min": 0
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
        min_value=0
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
        initial=None
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start and date_end:
            if date_start > date_end:
                self.add_error("date_start", "The start date must be earlier than the end date.")
            
            if date_start > date.today():
                self.add_error("date_start", "The start date cannot be in the future.")

            if date_end > date.today():
                self.add_error("date_end", "The end date cannot be in the future.")

class ReportsFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ("week", "Last Week"),
        ("month", "Last Month"),
        ("year", "Last Year"),
    ]
    INTERVAL_CHOICES = [
        ("day", "Daily"),
        # ("week", "Weekly"),
        # ("month", "Monthly"),
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


    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        # Dynamically set choices for interval field based on selected period
        period = self.initial.get("period", "month")
        if "period" in self.data:
            period = self.data.get("period")
        if period == "week":
            self.fields["interval"].choices = [
                ("day", "Daily"),
            ]
        elif period == "month":
            self.fields["interval"].choices = [
                ("day", "Daily"),
                ("week", "Weekly"),
            ]
        elif period == "year":
            self.fields["interval"].choices = [
                ("day", "Daily"),
                ("week", "Weekly"),
                ("month", "Monthly"),
            ]



                