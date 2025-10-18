# apps/finances/forms.py
from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # OG code(temporary removed): fields = ["name", "entry_type", "goal"]
        # this allows the website to work without category + goal link
        fields = ["name", "entry_type"]
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
