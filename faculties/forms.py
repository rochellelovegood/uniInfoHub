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

class UserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('ADMIN', 'Administrator'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    roll_no = forms.CharField(max_length=20, required=False)
    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, required=False)
    semester = forms.ChoiceField(choices=UserProfile.SEMESTER_CHOICES, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'roll_no', 'major', 'semester')
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'STUDENT':
            if not cleaned_data.get('roll_no'):
                self.add_error('roll_no', 'Roll number is required for students.')
            if not cleaned_data.get('major'):
                self.add_error('major', 'Major is required for students.')
            if not cleaned_data.get('semester'):
                self.add_error('semester', 'Semester is required for students.')

class UserEditForm(UserChangeForm):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('ADMIN', 'Administrator'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    roll_no = forms.CharField(max_length=20, required=False)
    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, required=False)
    semester = forms.ChoiceField(choices=UserProfile.SEMESTER_CHOICES, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'roll_no', 'major', 'semester')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')  # Remove password field
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'STUDENT':
            if not cleaned_data.get('roll_no'):
                self.add_error('roll_no', 'Roll number is required for students.')
            if not cleaned_data.get('major'):
                self.add_error('major', 'Major is required for students.')
            if not cleaned_data.get('semester'):
                self.add_error('semester', 'Semester is required for students.')