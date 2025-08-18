# uniHub/scholarships/views.py


from .models import Scholarship, UserProfile, Company, Testimonial
from django.shortcuts import render, redirect,get_object_or_404
from .models import Scholarship, UserProfile, Company, Testimonial, Announcement
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .forms import UserRegisterForm,CustomPasswordChangeForm,StudentProfileForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError


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
    context = {
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'scholarships/homepage.html', context)

@login_required
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
            
            # --- The critical redirect logic ---
            if hasattr(user, 'userprofile') and user.userprofile.role in ['FACULTY', 'ADMIN']:
                return redirect('faculties:faculty_dashboard_home') # <--- Must match faculty/urls.py
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
        'page_title': 'Register for UCSYers Hub'
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
                        return redirect('scholarships:homepage')
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
        context['companies'] = Company.objects.all()
        context['testimonials'] = Testimonial.objects.all()
        return context


def scholarship_detail(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    
    context = {
        'scholarship': scholarship,
        # Add any additional context you need
    }
    return render(request, 'scholarships/scholarship_detail.html', context)



from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
@login_required
def student_dashboard(request):
    user = request.user
    profile = user.userprofile  # Get the user's profile
    wishlist_scholarships = user.wishlist.all()

    # Initialize both forms
    password_form = CustomPasswordChangeForm(user=user)
    profile_form = StudentProfileForm(instance=profile)  # Add profile form

    if request.method == 'POST' and 'form_type' in request.POST:
        form_type = request.POST['form_type']

        if form_type == 'password_change':
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)

            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password = password_form.cleaned_data['new_password1']

                if not user.check_password(old_password):
                    messages.error(request, "Old password is incorrect")
                else:
                    # Save new password
                    user = password_form.save()

                    if user.check_password(new_password):
                        messages.success(request, "Password updated successfully!")
                        update_session_auth_hash(request, user)
                    else:
                        messages.error(request, "Password update failed!")

                return redirect('student_dashboard')

            else:

                context = {
                    'user': user,
                    'password_form': password_form,
                    'profile_form': profile_form,
                    'wishlist_scholarships': wishlist_scholarships,
                }
                return render(request, 'student_dashboard.html', context)

        elif form_type == 'profile_update':
            profile_form = StudentProfileForm(request.POST, instance=profile)

            if profile_form.is_valid():
                # Save the profile changes
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('student_dashboard')

            else:

                messages.error(request, "Please correct the errors below")
                context = {
                    'user': user,
                    'password_form': password_form,
                    'profile_form': profile_form,
                    'wishlist_scholarships': wishlist_scholarships,
                }
                return render(request, 'student_dashboard.html', context)


    context = {
        'user': user,
        'wishlist_scholarships': wishlist_scholarships,
        'password_form': password_form,
        'profile_form': profile_form,  # Add profile form to context
    }
    return render(request, 'student_dashboard.html', context)

from django.http import JsonResponse


@login_required
def toggle_wishlist(request, scholarship_id):
    scholarship = get_object_or_404(Scholarship, id=scholarship_id)
    user = request.user

    # Check if scholarship is in user's wishlist
    if user.wishlist.filter(id=scholarship_id).exists():
        user.wishlist.remove(scholarship)
        action = 'removed'
        message = f"Removed {scholarship.title} from your wishlist"
    else:
        user.wishlist.add(scholarship)
        action = 'added'
        message = f"Added {scholarship.title} to your wishlist"

    return JsonResponse({
        'status': 'success',
        'action': action,
        'message': message,
        'wishlist_count': user.wishlist.count()
    })


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Scholarship


@require_POST
@login_required
def remove_from_wishlist(request, scholarship_id):
    try:
        scholarship = Scholarship.objects.get(id=scholarship_id)
        request.user.wishlist.remove(scholarship)

        return JsonResponse({
            'success': True,
            'wishlist_count': request.user.wishlist.count()
        })

    except Scholarship.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Scholarship not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='login')
def announcements_list(request):
    """
    Displays a list of all announcements in a card format for students.
    """
    announcements = Announcement.objects.all().order_by('-posted_at')
    context = {
        'announcements': announcements,
        'title': 'Announcements'
    }
    return render(request, 'announcements_list.html', context)

