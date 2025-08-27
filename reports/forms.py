from django import forms
from students.models import Class

class AttendanceReportForm(forms.Form):
    class_obj = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label="Select Class",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
