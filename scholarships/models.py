# uniHub/scholarships/models.py
from django.db import models
from django.contrib.auth.models import User
class Scholarship(models.Model):
    """
    Represents a scholarship opportunity available to students.
    """
    title = models.CharField(max_length=200, help_text="The official title or name of the scholarship.")
    description = models.TextField(help_text="A comprehensive description of the scholarship, its purpose, and what it covers.")
    eligibility = models.TextField(
        help_text="Detailed criteria students must meet to be eligible (e.g., 'Minimum GPA 3.0', 'For undergraduate students', 'Myanmar citizen only')."
    )
    application_link = models.URLField(
        max_length=500,
        blank=True,
        help_text="Direct link to the external scholarship application website. Optional if a PDF brochure contains all application details."
    )
    deadline = models.DateField(help_text="The final date by which applications must be submitted.")

    # --- Fields for Filtering and Categorization ---
    min_gpa = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        help_text="Optional: The minimum GPA required for this scholarship (e.g., 3.0, 3.5). Leave blank if not applicable."
    )
    country = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Optional: The country for which this scholarship is intended (e.g., 'USA', 'Myanmar', 'UK')."
    )
    MAJOR_CHOICES = [
        ('SE', 'B.C.Sc. (Software Engineering)'),
        ('BIS', 'B.C.Sc. (Business Information Systems)'),
        ('KE', 'B.C.Sc. (Knowledge Engineering)'),
        ('HPC', 'B.C.Sc. (High Performance Computing)'),
        ('ES', 'B.C.Tech. (Embedded Systems)'),
        ('CN', 'B.C.Tech. (Communication and Networking)'),
        ('CSec', 'B.C.Tech. (Cyber Security)'),
    ]
    major = models.CharField(
        max_length=50, 
        choices=MAJOR_CHOICES, 
        default='SE', 
        help_text="The specific major(s) or department(s) for which the scholarship is applicable."
    )

    # --- Fields for Uploaded Files (Teacher-Provided) ---
    brochure_pdf = models.FileField(
        upload_to='scholarship_brochures/',
        null=True, blank=True,
        help_text="Optional: Upload a PDF document containing the scholarship brochure."
    )
    banner_image = models.ImageField(
        upload_to='scholarship_banners/',
        null=True, blank=True,
        help_text="Optional: Upload a relevant banner image or logo for the scholarship."
    )

    # --- Administrative Fields ---
    posted_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(
        default=True,
        help_text="Check this box if the scholarship is currently open for applications."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatically records the creation date and time."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically updates the date and time whenever the record is modified."
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['deadline', 'title']
        verbose_name_plural = "Scholarships"

# UserProfile model remains unchanged
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'), 
        ('ADMIN', 'Administrator'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    roll_no = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text="Your unique Roll Number (e.g., YKPT-XXXX). Required for Students."
    )

    MAJOR_CHOICES = [
        ('SE', 'B.C.Sc. (Software Engineering)'),
        ('BIS', 'B.C.Sc. (Business Information Systems)'),
        ('KE', 'B.C.Sc. (Knowledge Engineering)'),
        ('HPC', 'B.C.Sc. (High Performance Computing)'),
        ('ES', 'B.C.Tech. (Embedded Systems)'),
        ('CN', 'B.C.Tech. (Communication and Networking)'),
        ('CSec', 'B.C.Tech. (Cyber Security)'),
    ]
    major = models.CharField(max_length=50, choices=MAJOR_CHOICES, default='SE', blank=True, null=True)

    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 11)]
    semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile ({self.get_role_display()})'
