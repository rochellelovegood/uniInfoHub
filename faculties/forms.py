# faculties/forms.py
from django import forms
from scholarships.models import Company
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from scholarships.models import UserProfile

class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'website', 'logo', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., TechCorp Inc.'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g., https://www.techcorp.com'}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1'}),
        }
        labels = {
            'name': 'Company Name',
            'website': 'Company Website',
            'logo': 'Company Logo',
            'display_order': 'Display Order (Lower numbers appear first)',
        }

