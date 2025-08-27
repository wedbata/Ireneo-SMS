from django import forms
from .models import Applicant

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'email', 'phone_number', 'address', 'previous_school',
            'class_applying_for', 'birth_certificate', 'previous_report_card'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
