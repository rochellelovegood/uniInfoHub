# faculties/forms.py
from django import forms
from scholarships.models import Company,ACADEMIC_LEVEL_CHOICES 
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


class FacultyUserEditForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    is_active = forms.BooleanField(required=False)
    role = forms.CharField(max_length=20, required=False)
    roll_no = forms.CharField(max_length=20, required=False)
    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, required=False)
    academic_level = forms.ChoiceField(
        choices=ACADEMIC_LEVEL_CHOICES,
        label="Academic Level",
        required=False,
        help_text="Undergraduate or Graduate. Required for Students."
    )
    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

    def save(self, user, profile):
        # Update user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.is_active = self.cleaned_data['is_active']
        user.save()
        profile.role = self.cleaned_data['role']
        profile.roll_no = self.cleaned_data['roll_no']
        profile.major = self.cleaned_data['major']
        profile.semester = self.cleaned_data['semester']
        profile.save()