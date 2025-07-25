# uniHub/scholarships/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile # Make sure UserProfile is imported
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
        """
        Overrides the save method to create both the User and UserProfile.
        """
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