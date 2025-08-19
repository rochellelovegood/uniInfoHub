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


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'file', 'url', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if resource_type in ['PDF', 'SLIDES', 'OTHER'] and not file:
            self.add_error('file', f"A file is required for {dict(self.fields['resource_type'].choices)[resource_type]} resources")
        if resource_type == 'LINK' and not url:
            self.add_error('url', "A URL is required for Link resources")
        if resource_type == 'VIDEO' and not (file or url):
            self.add_error(None, "Video resources require either a file or URL")

        return cleaned_data