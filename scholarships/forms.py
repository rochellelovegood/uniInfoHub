from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, Scholarship, Announcement, ACADEMIC_LEVEL_CHOICES
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="Role",
        initial='STUDENT',
        widget=forms.RadioSelect
    )
    roll_no = forms.CharField(
        max_length=20,
        label="Your Roll No",
        required=False,
        help_text="Must start with 'YKPT' (e.g., YKPT-XXXX). Required for Students."
    )
    major = forms.ChoiceField(
        choices=UserProfile.MAJOR_CHOICES,
        label="Major",
        required=False
    )
    # CORRECTED: Replaced the duplicate major field with the new academic_level field.
    academic_level = forms.ChoiceField(
        choices=ACADEMIC_LEVEL_CHOICES,
        label="Academic Level",
        required=False,
        help_text="Undergraduate or Graduate. Required for Students."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no')
        if roll_no:
            if not roll_no.startswith('YKPT'):
                raise forms.ValidationError("Roll number must start with 'YKPT'.")
            if UserProfile.objects.filter(roll_no=roll_no).exists():
                raise forms.ValidationError("This roll number is already registered.")
        return roll_no

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        roll_no = cleaned_data.get('roll_no')
        major = cleaned_data.get('major')
        # UPDATED: Getting the new academic_level data
        academic_level = cleaned_data.get('academic_level')

        if role == 'STUDENT':
            if not roll_no:
                self.add_error('roll_no', "Roll number is required for Students.")
            if not major:
                self.add_error('major', "Major is required for Students.")
            # UPDATED: Now checks academic_level instead of semester
            if not academic_level:
                self.add_error('academic_level', "Academic level is required for Students.")
        else:
            cleaned_data['roll_no'] = None
            cleaned_data['major'] = None
            # UPDATED: Clears academic_level for non-students
            cleaned_data['academic_level'] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile_data = {
                'user': user,
                'role': self.cleaned_data['role'],
                'roll_no': self.cleaned_data.get('roll_no'),
                'major': self.cleaned_data.get('major'),
                # UPDATED: Passes the new academic_level data to the UserProfile
                'academic_level': self.cleaned_data.get('academic_level'),
            }
            UserProfile.objects.create(**profile_data)
        return user


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        # Note: '__all__' automatically includes the new 'level' field
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scholarship Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description...'}),
            'eligibility': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Eligibility criteria...'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/apply'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'min_gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 3.0'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USA, Myanmar'}),
            'major': forms.Select(attrs={'class': 'form-select'}),
           
            'level': forms.Select(attrs={'class': 'form-select'}),
            'brochure_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # REMOVED: major_department widget, as it does not exist in the model
        }
        labels = {
            'min_gpa': 'Minimum GPA (Optional)',
            'country': 'Target Country (Optional)',
            'major': 'Target Major',
            # ADDED: New label for the 'level' field
            'level': 'Academic Level',
            'brochure_pdf': 'Brochure PDF (Optional)',
            'banner_image': 'Banner Image (Optional)',
            'is_active': 'Active Scholarship',
            # REMOVED: major_department label, as it does not exist in the model
        }
        exclude = ['posted_by', 'created_at', 'updated_at', 'is_active', 'wishlisted_by']


class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        try:
            validate_password(password, self.user)
        except ValidationError as e:
            self.add_error('new_password1', e)
        return password


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # UPDATED: Replaced 'semester' with 'academic_level'
        fields = ['major', 'academic_level']
        widgets = {
            'major': forms.Select(choices=UserProfile.MAJOR_CHOICES),
            # UPDATED: Replaced 'semester' widget with 'academic_level'
            'academic_level': forms.Select(choices=ACADEMIC_LEVEL_CHOICES),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'place', 'time','attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }