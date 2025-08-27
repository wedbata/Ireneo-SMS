from django import forms
from .models import Expense, ExpenseCategory

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description', 'paid_to', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
