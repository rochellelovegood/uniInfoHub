# faculties/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from scholarships.models import UserProfile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from scholarships.forms import ScholarshipForm, AnnouncementForm
from scholarships.models import Scholarship, UserProfile, Announcement,Company
from datetime import date
from django.db.models import Q 
from django.shortcuts import render, redirect
from .forms import CompanyForm
from django.shortcuts import render, redirect
from .forms import CompanyForm, ResourceForm
from django.shortcuts import render, get_object_or_404
from itertools import chain
from operator import attrgetter
# This helper function is specific to faculty access, so it lives here
def is_faculty_or_admin(user):
    """
    Checks if the user has a FACULTY or ADMIN role.
    """
    if not user.is_authenticated:
        return False
    # Check if the user has a userprofile before accessing its attributes
    if not hasattr(user, 'userprofile'):
        return False
    return user.userprofile.role in ['FACULTY', 'ADMIN']

@login_required
def faculty_dashboard_home(request):
    # Only faculty can access this dashboard
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'FACULTY':
        # You'll want to handle this with a redirect or an error page
        return redirect('home')
        
    # Fetch recent objects, filtered by the current user
    # Note: We can't filter the Company model by user as it lacks the 'posted_by' field.
    my_scholarships = Scholarship.objects.filter(posted_by=request.user)
    for obj in my_scholarships:
        obj.type = 'Scholarship'
    
    my_announcements = Announcement.objects.filter(posted_by=request.user)
    for obj in my_announcements:
        obj.type = 'Announcement'

    all_activities = sorted(
        chain(my_scholarships, my_announcements),
        key=attrgetter('created_at'), # The Announcement model has this field.
        reverse=True
    )

    # Get the 3 most recent activities for the dashboard
    recent_activities = all_activities[:3]
  
    context = {
        'my_scholarships': my_scholarships,
        'my_companies': Company.objects.all(), # Keep this for the separate tab
        'recent_activities': recent_activities, 
      
        'total_count':   my_scholarships.count() + my_announcements.count()+ Company.objects.count(),
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def post_scholarship(request):
    """
    Handles posting a new scholarship.
    This view is specifically for faculty/admin users.
    """
    if not is_faculty_or_admin(request.user):
        messages.error(request, "You do not have permission to post scholarships.")
        return redirect('scholarships:list')

    if request.method == 'POST':
       
        form = ScholarshipForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                scholarship = form.save(commit=False)
                # Assign the current User object directly, since there is no FacultyProfile
                scholarship.posted_by = request.user
                scholarship.save()
                messages.success(request, 'Scholarship posted successfully!')
                return redirect('faculties:faculty_dashboard_home') # Redirect to dashboard after posting
            except Exception as e:
                # Catch any unexpected errors during save
                messages.error(request, f"An unexpected error occurred: {e}")
        else:
            # Log the errors to the console for debugging
            print("Form errors:", form.errors)
            # Re-render the form with errors
            messages.error(request, 'Please correct the errors below to post the scholarship.')

            # We can also add specific field errors to the messages framework for better user feedback
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")

    else: # GET request
        form = ScholarshipForm()

    context = {
        'form': form,
        'page_title': 'Post New Scholarship'
    }
    return render(request, 'dashboard/post_scholarship.html', context)


def logout_view(request):
    """
    Logs out the current user and redirects to the home view.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    
    return redirect('home')
@login_required
def edit_scholarship(request, scholarship_id):
    """
    Handles editing an existing scholarship.
    Only allows editing by the original poster or admin.
    """
    if not is_faculty_or_admin(request.user):
        messages.error(request, "You do not have permission to edit scholarships.")
        return redirect('scholarships:list')

    try:
        scholarship = Scholarship.objects.get(id=scholarship_id)
        
        # Check if the current user is the owner or an admin
        if scholarship.posted_by != request.user and request.user.userprofile.role != 'ADMIN':
            messages.error(request, "You can only edit scholarships you've posted.")
            return redirect('faculties:faculty_dashboard_home')

        if request.method == 'POST':
            form = ScholarshipForm(request.POST, request.FILES, instance=scholarship)
            if form.is_valid():
                form.save()
                messages.success(request, 'Scholarship updated successfully!')
                return redirect('faculties:faculty_dashboard_home')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ScholarshipForm(instance=scholarship)

        context = {
            'form': form,
            'scholarship': scholarship,
            'page_title': 'Edit Scholarship'
        }
        return render(request, 'dashboard/edit_scholarship.html', context)

    except Scholarship.DoesNotExist:
        messages.error(request, "The scholarship you're trying to edit doesn't exist.")
        return redirect('faculties:faculty_dashboard_home')


@login_required
def delete_scholarship(request, scholarship_id):
    """
    Handles deleting a scholarship.
    Only allows deletion by the original poster or admin.
    """
    if not is_faculty_or_admin(request.user):
        messages.error(request, "You do not have permission to delete scholarships.")
        return redirect('scholarships:list')

    try:
        scholarship = Scholarship.objects.get(id=scholarship_id)
        
        # Check if the current user is the owner or an admin
        if scholarship.posted_by != request.user and request.user.userprofile.role != 'ADMIN':
            messages.error(request, "You can only delete scholarships you've posted.")
            return redirect('faculties:faculty_dashboard_home')

        if request.method == 'POST':
            scholarship.delete()
            messages.success(request, 'Scholarship deleted successfully!')
            return redirect('faculties:faculty_dashboard_home')

        # If GET request, show confirmation page
        context = {
            'scholarship': scholarship,
            'page_title': 'Confirm Deletion'
        }
        return render(request, 'dashboard/confirm_delete.html', context)

    except Scholarship.DoesNotExist:
        messages.error(request, "The scholarship you're trying to delete doesn't exist.")
        return redirect('faculties:faculty_dashboard_home')
    

@login_required
def scholarship_list_view(request):

    today = date.today()
    scholarships = Scholarship.objects.filter(is_active=True, deadline__gte=today).order_by('deadline')

    # Get filter/search parameters from the URL's GET request (e.g., from the form)
    query = request.GET.get('q') # General search term (e.g., "science scholarship")
    min_gpa = request.GET.get('gpa') # User wants scholarships requiring this GPA or lower
    country = request.GET.get('country') # User wants scholarships for this country
    major = request.GET.get('major') # User wants scholarships for this major/department
    deadline_before_str = request.GET.get('deadline_before') # User wants scholarships with a deadline before this date

    # --- Apply Search Filter ---
    if query:
        scholarships = scholarships.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(eligibility__icontains=query) |
            Q(country__icontains=query) |
            Q(major_department__icontains=query)
        ).distinct() # Use distinct to avoid duplicate results if a scholarship matches multiple Q conditions

    # --- Apply GPA Filter ---
    # Filters for scholarships where their 'min_gpa' is less than or equal to the entered GPA,
    # OR where the scholarship doesn't specify a min_gpa (meaning it's open to all GPAs).
    if min_gpa:
        try:
            min_gpa_float = float(min_gpa)
            scholarships = scholarships.filter(Q(min_gpa__lte=min_gpa_float) | Q(min_gpa__isnull=True))
        except ValueError:
            pass # Ignore invalid GPA input (e.g., if user types text)

    # --- Apply Country Filter ---
    if country:
        scholarships = scholarships.filter(country__icontains=country) # Case-insensitive contains

    # --- Apply Major/Department Filter ---
    if major:
        scholarships = scholarships.filter(major_department__icontains=major)

    # --- Apply 'Deadline Before' Filter ---
    if deadline_before_str:
        try:
            # Convert string date from input (YYYY-MM-DD) to a date object
            target_date = date.fromisoformat(deadline_before_str)
            scholarships = scholarships.filter(deadline__lte=target_date) # Deadline is less than or equal to target date
        except ValueError:
            pass # Ignore invalid date format

    # Prepare context to pass data to the template
    context = {
        'scholarships': scholarships,
        'query': query or '', # Pass back current search query to display in the form
        'min_gpa': min_gpa or '',
        'country': country or '',
        'major': major or '',
        'deadline_before_str': deadline_before_str or '', # Pass back current deadline filter
        'semester_choices': UserProfile.SEMESTER_CHOICES, # <--- Pass this to the template
        'semester': request.GET.get('semester') 
    }
    return render(request, 'scholarships.html', context)



@login_required(login_url='login')
def post_company(request):
    """
    Handles posting a new company opportunity.
    """
    if request.method == 'POST':
        # IMPORTANT: You must pass request.FILES for file uploads.
        form = CompanyForm(request.POST, request.FILES) 
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user 
            company.save()
            return redirect('faculties:faculty_dashboard_home') 
        else:
            # For debugging, you can print the form errors to your console.
            print("Form is not valid:", form.errors)
    else:
        form = CompanyForm()
        
    context = {'form': form, 'title': 'Post New Company'}
    return render(request, 'dashboard/post_company.html', context)

# In views.py
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        return redirect('faculties:faculty_dashboard')
    return redirect('faculties:faculty_dashboard')
# You'll need this import later to display them


@login_required(login_url='login')
def post_announcement(request):
    """
    Handles posting a new announcement.
    """
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.save()
            return redirect('faculties:faculty_dashboard_home') # Redirect to the dashboard
    else:
        form = AnnouncementForm()

    context = {'form': form, 'title': 'Post New Announcement'}
    # Template path is now in the faculties app
    return render(request, 'dashboard/post_announcement.html', context)

def is_faculty(user):
    return user.userprofile.role in ['FACULTY', 'ADMIN']
