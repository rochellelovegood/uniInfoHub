# uniHub/scholarships/views.py

from .models import Scholarship # Import your Scholarship model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.db.models import Q # Keep this for scholarship_list
from datetime import date # Keep this for scholarship_lis
from .forms import UserRegisterForm # <--- This is now correct

# uniHub/uniHub/views.py

from django.shortcuts import render

from django.shortcuts import render
# from .models import Scholarship # You'll need this for scholarship_list later

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
def scholarship_list(request):
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


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verify the user's role matches selection
            if user.role == role:
                # Additional validation for students
                if role == 'STUDENT':
                    wifi_email = request.POST.get('wifi_email', '')
                    if not wifi_email.startswith('WIFI'):
                        messages.error(request, "Student email must start with 'WIFI'")
                        return redirect('login')

                login(request, user)

                # Redirect based on role
                if role == 'STUDENT':
                    return redirect('student_dashboard')
                elif role == 'FACULTY':
                    return redirect('faculty_dashboard')
                elif role == 'ADMIN':
                    return redirect('admin_dashboard')
            else:
                messages.error(request, "This account doesn't have the selected role")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')