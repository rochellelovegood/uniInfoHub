# faculties/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from scholarships.forms import ScholarshipForm, AnnouncementForm
from scholarships.models import Scholarship, UserProfile, Announcement,Company
from datetime import date
from django.db.models import Q 
from django.shortcuts import render, redirect
from .forms import CompanyForm, FacultyUserEditForm
from django.shortcuts import render, redirect
from .forms import CompanyForm
from django.shortcuts import render, get_object_or_404
from itertools import chain
from operator import attrgetter
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


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
        'my_companies': Company.objects.all(), 
        'my_announcements': my_announcements,# Keep this for the separate tab
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
        return redirect('faculties:faculty_dashboard_home')
    return redirect('faculties:faculty_dashboard_home')





@login_required
@user_passes_test(is_faculty_or_admin)
def post_announcement(request):
    if request.method == 'POST':
        # CRITICAL FIX: Add 'request.FILES' to the form instance
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.save()
            
            # Note: The form.save_m2m() call is not needed unless you have a ManyToMany field.
            # I have removed it here for cleaner code.
            
            messages.success(request, 'Announcement posted successfully.')
            return redirect('faculties:faculty_dashboard_home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnnouncementForm()

    context = {'form': form, 'title': 'Post New Announcement'}
    return render(request, 'dashboard/post_announcement.html', context)
def is_faculty(user):
    return user.userprofile.role in ['FACULTY', 'ADMIN']

def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('faculties:faculty_dashboard_home')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'dashboard/post_announcement.html', {'form': form, 'announcement': announcement})

# NEW: View to handle deleting an announcement
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
    return redirect('faculties:faculty_dashboard_home')

@login_required
def manage_users(request):
    if not request.user.is_authenticated or not request.user.userprofile.role == 'FACULTY':
        raise PermissionDenied

    # Get search query from URL parameters
    search_query = request.GET.get('roll_no', '').strip()

    # Start with all student users
    student_users = User.objects.filter(
        userprofile__role='STUDENT'
    ).select_related('userprofile').order_by('-date_joined')

    # Apply search filter if query exists
    if search_query:
        student_users = student_users.filter(
            Q(userprofile__roll_no__icontains=search_query)
        )

    return render(request, 'manage_users.html', {
        'users': student_users
    })

@login_required
def edit_user(request, user_id):
    try:
        profile = request.user.userprofile
        if profile.role not in ['FACULTY', 'ADMIN']:
            raise PermissionDenied
    except UserProfile.DoesNotExist:
        raise PermissionDenied

    edited_user = get_object_or_404(User, id=user_id)  # Changed variable name
    user_profile = edited_user.userprofile  # Updated reference

    # Prevent editing superusers
    if edited_user.is_superuser:  # Updated reference
        raise PermissionDenied("Cannot edit superuser accounts")

    if request.method == 'POST':
        # Create form with POST data and profile instance
        form = FacultyUserEditForm(request.POST, profile=user_profile)
        if form.is_valid():
            form.save(edited_user, user_profile)  # Updated reference
            return redirect('faculties:manage_users')
    else:
        # Initialize form with initial data
        form = FacultyUserEditForm(profile=user_profile, initial={
            'username': edited_user.username,  # Updated reference
            'email': edited_user.email,  # Updated reference
            'is_active': edited_user.is_active,  # Updated reference
            'role': user_profile.role,
            'roll_no': user_profile.roll_no,
            'major': user_profile.major,
        })

    return render(request, 'dashboard/edit_user.html', {
        'form': form,
        'edited_user': edited_user  # Changed key name to avoid conflict
    })

@login_required
@require_POST
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"Account {username} has been deleted successfully")
    return redirect('faculties:manage_users')