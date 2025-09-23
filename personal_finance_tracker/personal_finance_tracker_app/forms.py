# this form was created to better use Django's automatic plugins
# such as managing inputs and making sure decimal amounts are correct

from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["date", "transaction", "amount", "category", "description", "goals"]
        # use a widget to tell Djagno to ignore the default settings and use a dropdown menu
        widgets = {
            'goals': forms.Select(choices=[('yes', 'Yes'), ('no', 'No')])
        }
