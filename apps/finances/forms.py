from django import forms

from .models import Category, Entry


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
    """
    entry_type = forms.ChoiceField(
        choices=[("income", "Income"), ("expense", "Expense")],
        initial="income"
        )
        """
    class Meta:
        model = Entry
        fields = ["date", "name", "amount", "entry_type", "category", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "date",
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
                }
            ),
            "entry_type": forms.RadioSelect(
                attrs={
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
