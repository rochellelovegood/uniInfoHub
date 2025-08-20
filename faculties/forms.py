# faculties/forms.py
from django import forms
from scholarships.models import Company, ACADEMIC_LEVEL_CHOICES, UserProfile

# Note: The following imports are not used in the provided code,
# but might be needed for other forms in this file.
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


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


# forms.py
class FacultyUserEditForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    is_active = forms.BooleanField(required=False)
    role = forms.CharField(max_length=20, required=False)
    roll_no = forms.CharField(max_length=20, required=False)
    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, required=False)

    # Replace ChoiceField with Boolean fields for checkboxes
    academic_level_undergraduate = forms.BooleanField(
        required=False,
        label="Undergraduate"
    )
    academic_level_graduate = forms.BooleanField(
        required=False,
        label="Graduate"
    )

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        # Set initial values for checkboxes based on profile data
        if self.profile and self.profile.academic_level:
            if self.profile.academic_level == 'UNDERGRADUATE':
                self.fields['academic_level_undergraduate'].initial = True
            elif self.profile.academic_level == 'GRADUATE':
                self.fields['academic_level_graduate'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        undergrad = cleaned_data.get('academic_level_undergraduate')
        grad = cleaned_data.get('academic_level_graduate')

        # Validate that only one academic level is selected
        if undergrad and grad:
            raise forms.ValidationError("Please select only one academic level.")

        # Set the academic_level value based on checkbox selection
        if undergrad:
            cleaned_data['academic_level'] = 'UNDERGRADUATE'
        elif grad:
            cleaned_data['academic_level'] = 'GRADUATE'
        else:
            cleaned_data['academic_level'] = ''

        return cleaned_data

    def save(self, user, profile):
        # Update user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.is_active = self.cleaned_data['is_active']
        user.save()

        # Update user profile with cleaned data from the form
        profile.role = self.cleaned_data['role']
        profile.roll_no = self.cleaned_data['roll_no']
        profile.major = self.cleaned_data['major']

        # Save the academic_level field to the profile
        profile.academic_level = self.cleaned_data['academic_level']
        profile.save()