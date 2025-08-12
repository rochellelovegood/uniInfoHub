# uniHub/scholarships/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile,Scholarship
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



from .models import UserProfile,Scholarship, Announcement
import re
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")

    # Add the new 'role' field to the form
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, label="Role", initial='STUDENT',
                             widget=forms.RadioSelect) 

    # Make roll_no not required by default in the form,
    # we'll enforce it conditionally in clean()
    roll_no = forms.CharField(
        max_length=20, 
        label="Your Roll No",
        required=False, # <--- IMPORTANT: No longer required here
        help_text="Must start with 'YKPT' (e.g., YKPT-XXXX). Required for Students."
    )

    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, label="Major", required=False) # Make optional
    semester = forms.ChoiceField(choices=UserProfile.SEMESTER_CHOICES, label="Semester", required=False) # Make optional

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_roll_no(self):
        """
        Custom validation for roll_no: must start with 'YKPT' and be unique.
        This method will run even if the field is not required.
        """
        roll_no = self.cleaned_data.get('roll_no')
        if roll_no: # Only validate if roll_no is provided
            if not roll_no.startswith('YKPT'):
                raise forms.ValidationError("Roll number must start with 'YKPT'.")
            if UserProfile.objects.filter(roll_no=roll_no).exists():
                raise forms.ValidationError("This roll number is already registered.")
        return roll_no

    def clean(self):
        """
        Overall form cleaning, including conditional validation for roll_no and major/semester.
        """
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        roll_no = cleaned_data.get('roll_no')
        major = cleaned_data.get('major')
        semester = cleaned_data.get('semester')

        if role == 'STUDENT':
            # Roll number is required for students
            if not roll_no:
                self.add_error('roll_no', "Roll number is required for Students.")
            # Major and Semester are also required for Students
            if not major:
                self.add_error('major', "Major is required for Students.")
            if not semester:
                self.add_error('semester', "Semester is required for Students.")
        else:
            # If not a student, clear roll_no, major, and semester if they were accidentally filled
            # This prevents saving irrelevant data for non-students
            if 'roll_no' in cleaned_data:
                cleaned_data['roll_no'] = None
            if 'major' in cleaned_data:
                cleaned_data['major'] = None
            if 'semester' in cleaned_data:
                cleaned_data['semester'] = None

        return cleaned_data


    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

            # Prepare data for UserProfile
            profile_data = {
                'user': user,
                'role': self.cleaned_data['role'],
                'roll_no': self.cleaned_data.get('roll_no'), # Use .get() as it might be None
                'major': self.cleaned_data.get('major'),
                'semester': self.cleaned_data.get('semester'),
            }
            UserProfile.objects.create(**profile_data)
        return user


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = '__all__' # Use all fields from the Scholarship model
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scholarship Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description...'}),
            'eligibility': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Eligibility criteria...'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/apply'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # HTML5 date input
            'min_gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 3.0'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USA, Myanmar'}),
            'major': forms.Select(attrs={'class': 'form-select'}), # For major in Scholarship model
            'major_department': forms.Select(attrs={'class': 'form-select'}), # For major_department in Scholarship model
            'brochure_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'min_gpa': 'Minimum GPA (Optional)',
            'country': 'Target Country (Optional)',
            'major': 'Target Major', # Or 'Target Degree Program'
            'major_department': 'Specific Department/Field (Optional)',
            'brochure_pdf': 'Brochure PDF (Optional)',
            'banner_image': 'Banner Image (Optional)',
            'is_active': 'Active Scholarship',
        }
        exclude = ['posted_by', 'created_at', 'updated_at', 'is_active']



class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        try:
            # Validate against Django's password validators
            validate_password(password, self.user)
        except ValidationError as e:
            # Add validation errors to the form
            self.add_error('new_password1', e)
        return password



class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['major', 'semester']
        widgets = {
            'semester': forms.Select(choices=UserProfile.SEMESTER_CHOICES),
            'major': forms.Select(choices=UserProfile.MAJOR_CHOICES),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'place', 'time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})

        }