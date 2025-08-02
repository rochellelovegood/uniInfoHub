# uniHub/scholarships/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Q 
from datetime import date # Keep this for scholarship_lis
from .forms import UserRegisterForm, ScholarshipForm # <<< Import ScholarshipForm
from .models import Scholarship, UserProfile# <--- This is now correct
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import render
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
# from .models import Scholarship # You'll need this for scholarship_list later


def is_faculty_or_admin(user):
    # Check if user is authenticated first
    if not user.is_authenticated:
        return False
    # Ensure the user has a UserProfile
    if not hasattr(user, 'userprofile'):
        return False
    # Check the role in the UserProfile
    return user.userprofile.role in ['FACULTY', 'ADMIN']
def home_view(request):
    """
    Renders the main home page of OpportunityHub.
    This page will showcase sample content and introduce the site.
    """
    context = {
        'page_title': 'Unlock Your Potential', # This will be the main title in the hero section
        'intro_message': 'Discover scholarships, events, and resources to propel your academic and career journey at UCSY.', # This will be the subtitle
    }
    return render(request, 'home.html', context)
def scholarship_list_view(request):
    """
    Displays a list of active scholarships, with options for filtering and searching.
    """
    # Start with all active scholarships whose deadline has not passed, ordered by deadline (soonest first)
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
    return render(request, 'scholarships/scholarship_list.html', context)

# NEW: register_view (moved from users/views.py)
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        'page_title': 'Register for OpportunityHub'
    }
    return render(request, 'registration/register.html', context)


@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role_selected_in_form = request.POST.get('role') # Get the role selected by the user in the form

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user has a UserProfile
            if hasattr(user, 'userprofile'):
                user_actual_role = user.userprofile.role # Get the actual role from the UserProfile

                # Verify the user's actual role matches the role selected in the login form
                if user_actual_role == role_selected_in_form:
                    # REMOVED: wifi_email validation as requested
                    
                    login(request, user) # Log the user in

                    # Redirect based on the user's actual role
                    if user_actual_role == 'STUDENT':
                        messages.success(request, f'Welcome, {user.username} (Student)!')
                        return redirect('student_dashboard') # Assuming 'student_dashboard' exists
                    elif user_actual_role == 'FACULTY':
                        messages.success(request, f'Welcome, {user.username} (Faculty)!')
                        # Redirect Faculty to scholarships list page
                        return redirect('faculties:faculty_dashboard_home') # Redirect to the scholarships list
                    elif user_actual_role == 'ADMIN':
                        messages.success(request, f'Welcome, {user.username} (Admin)!')
                        return redirect('admin:index') # Redirect to Django admin page
                else:
                    messages.error(request, f"Your account is registered as {user_actual_role}, but you selected {role_selected_in_form}. Please select the correct role.")
            else:
                # This case should ideally not happen if every User has a UserProfile
                messages.error(request, "User profile not found for this account.")
        else:
            messages.error(request, "Invalid username or password.")

    # Pass the role choices to the template for the dropdown/radio buttons
    from .models import UserProfile
    role_choices = UserProfile.ROLE_CHOICES
    return render(request, 'registration/login.html', {'role_choices': role_choices})


def scholarship_list_view(request):
    """
    Displays a list of active scholarships, with options for filtering, searching, and sorting.
    """
    scholarships = Scholarship.objects.filter(is_active=True).order_by('-created_at') # Order by most recent first
    # Add filtering/searching logic later if needed
    context = {
        'scholarships': scholarships,
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'scholarships/scholarship_list.html', context)


# --- NEW: Post Scholarship View (Admin/Faculty Access) ---
@login_required # User must be logged in
@user_passes_test(is_faculty_or_admin, login_url='/login/') # Only faculty/admin can access. Redirects to login if not.
@csrf_protect
def post_scholarship_view(request):
    if request.method == 'POST':
        # Files are in request.FILES for FileField and ImageField
        form = ScholarshipForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scholarship posted successfully!')
            return redirect('scholarships:list') # Redirect to the scholarship list page
        else:
            messages.error(request, 'Error posting scholarship. Please check the form.')
    else:
        form = ScholarshipForm() # Empty form for GET request
    return render(request, 'scholarships/post_scholarship.html', {'form': form})

def logout_view(request):
    """
    Logs out the current user and redirects to the home view.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    
    return redirect('home')
