# uniHub/scholarships/forms.py

# uniHub/scholarships/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User # <--- ADD THIS LINE
from .models import UserProfile
import re

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    roll_no = forms.CharField(max_length=20, label="Your Roll No",
                              help_text="Must start with 'YKPT' (e.g., YKPT-001)")
    major = forms.ChoiceField(choices=UserProfile.MAJOR_CHOICES, label="Major")
    semester = forms.ChoiceField(choices=UserProfile.SEMESTER_CHOICES, label="Semester")

    class Meta(UserCreationForm.Meta):
        model = User # Ensure User is imported if not already. This is usually from django.contrib.auth.models
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        from django.contrib.auth.models import User # Import User model here if not at top of file
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no')
        if not roll_no.startswith('YKPT'):
            raise forms.ValidationError("Roll number must start with 'YKPT'.")
        if UserProfile.objects.filter(roll_no=roll_no).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll_no

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                roll_no=self.cleaned_data['roll_no'],
                major=self.cleaned_data['major'],
                semester=self.cleaned_data['semester']
            )
        return user