# uniHub/scholarships/views.py

from .models import Scholarship, UserProfile, Company, Testimonial
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .forms import UserRegisterForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

def is_faculty_or_admin(user):
    """Checks if the user has a FACULTY or ADMIN role."""
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'userprofile'):
        return False
    return user.userprofile.role in ['FACULTY', 'ADMIN']


def home_view(request):
    """Renders the main home page of OpportunityHub."""
    context = {
        'page_title': 'Unlock Your Potential',
        'intro_message': 'Discover scholarships, events, and resources to propel your academic and career journey at UCSY.',
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'home.html', context)
def homepage(request):
   
   
    return render(request, 'scholarships/homepage.html')


def scholarship_list_view(request):
    """Displays a list of active scholarships, with options for filtering and searching."""
    today = date.today()
    scholarships = Scholarship.objects.filter(is_active=True, deadline__gte=today).order_by('deadline')
    
    query = request.GET.get('q')
    min_gpa = request.GET.get('gpa')
    country = request.GET.get('country')
    major = request.GET.get('major')
    deadline_before_str = request.GET.get('deadline_before')

    if query:
        scholarships = scholarships.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(eligibility__icontains=query) | Q(country__icontains=query) | Q(major_department__icontains=query)
        ).distinct()

    if min_gpa:
        try:
            min_gpa_float = float(min_gpa)
            scholarships = scholarships.filter(Q(min_gpa__lte=min_gpa_float) | Q(min_gpa__isnull=True))
        except ValueError:
            pass

    if country:
        scholarships = scholarships.filter(country__icontains=country)

    if major:
        scholarships = scholarships.filter(major_department__icontains=major)

    if deadline_before_str:
        try:
            target_date = date.fromisoformat(deadline_before_str)
            scholarships = scholarships.filter(deadline__lte=target_date)
        except ValueError:
            pass
    
    context = {
        'scholarships': scholarships,
        'query': query or '',
        'min_gpa': min_gpa or '',
        'country': country or '',
        'major': major or '',
        'deadline_before_str': deadline_before_str or '',
        'semester_choices': UserProfile.SEMESTER_CHOICES,
        'semester': request.GET.get('semester'),
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'scholarships/scholarship_list.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            
            if hasattr(user, 'userprofile') and user.userprofile.role in ['FACULTY', 'ADMIN']:
                return redirect('faculties:faculty_dashboard_home')
            else:
                return redirect('scholarships:list')
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
        role_selected_in_form = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if hasattr(user, 'userprofile'):
                user_actual_role = user.userprofile.role
                if user_actual_role == role_selected_in_form:
                    login(request, user)
                    if user_actual_role == 'STUDENT':
                        messages.success(request, f'Welcome, {user.username} (Student)!')
                        return redirect('scholarships:list')
                    elif user_actual_role == 'FACULTY':
                        messages.success(request, f'Welcome, {user.username} (Faculty)!')
                        return redirect('faculties:faculty_dashboard_home')
                    elif user_actual_role == 'ADMIN':
                        messages.success(request, f'Welcome, {user.username} (Admin)!')
                        return redirect('admin:index')
                else:
                    messages.error(request, f"Your account is registered as {user_actual_role}, but you selected {role_selected_in_form}. Please select the correct role.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    from .models import UserProfile
    role_choices = UserProfile.ROLE_CHOICES
    return render(request, 'registration/login.html', {'role_choices': role_choices})


def logout_view(request):
    """Logs out the current user and redirects to the home view."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    
    return redirect('home')


class InternshipsView(TemplateView):
    """A class-based view to display internships and testimonials."""
    template_name = 'internships.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all active companies and testimonials to display
        context['companies'] = Company.objects.all()
        context['testimonials'] = Testimonial.objects.all()
        return context
