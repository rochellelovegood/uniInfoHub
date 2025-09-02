# uniHub/scholarships/views.py


from .models import Scholarship, UserProfile, Company, Testimonial, Announcement, ACADEMIC_LEVEL_CHOICES
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.db.models import Q, Case, When, IntegerField
from datetime import date, timedelta
from .forms import UserRegisterForm, CustomPasswordChangeForm, StudentProfileForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.dateparse import parse_date
import json # Corrected: Moved import to the top of the file

def is_faculty_or_admin(user):
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'userprofile'):
        return False
    return user.userprofile.role in ['FACULTY', 'ADMIN']


def home_view(request):
    context = {
        'page_title': 'UCSYer Hub - Home',
        'intro_message': 'Discover scholarships, events, and resources to propel your academic and career journey at UCSY.',
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'home.html', context)


def homepage(request):
    context = {
        'is_faculty_or_admin': is_faculty_or_admin(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'scholarships/homepage.html', context)



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta
from .models import Scholarship


@login_required
def scholarship_list_view(request):
    # Fetch all scholarships
    scholarships_list = Scholarship.objects.all()

    # Get filter and sort parameters from the request
    search_query = request.GET.get('search', '')
    selected_deadline = request.GET.get('deadline', '')
    selected_level = request.GET.get('level', '')
    major = request.GET.get('major', '')
    min_gpa_query = request.GET.get('min_gpa', '')
    sort_by = request.GET.get('sort', 'deadline')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Apply filters
    month_mapping = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }

    is_date_search = False

    # Split the query to handle "Sep 2025"
    query_parts = search_query.split()

    if len(query_parts) == 2:
        month_part = query_parts[0].lower()
        year_part = query_parts[1]

        if month_part in month_mapping and year_part.isdigit():
            month_int = month_mapping[month_part]
            year_int = int(year_part)
            scholarships_list = scholarships_list.filter(
                deadline__month=month_int,
                deadline__year=year_int
            )
            is_date_search = True

    if not is_date_search:
        # Check for month name or number as a single word
        if search_query.lower() in month_mapping:
            month_int = month_mapping[search_query.lower()]
            scholarships_list = scholarships_list.filter(deadline__month=month_int)
            is_date_search = True
        else:
            try:
                search_int = int(search_query)
                if 1 <= search_int <= 12:  # Check for month number
                    scholarships_list = scholarships_list.filter(deadline__month=search_int)
                    is_date_search = True
                elif 1900 <= search_int <= 2100:  # Check for year number
                    scholarships_list = scholarships_list.filter(deadline__year=search_int)
                    is_date_search = True
            except (ValueError, TypeError):
                pass

    if not is_date_search and search_query:
        scholarships_list = scholarships_list.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(
                country__icontains=search_query))


    if selected_level:
            scholarships_list = scholarships_list.filter(level=selected_level)

    if min_gpa_query:
        try:
            min_gpa_value = float(min_gpa_query)
            scholarships_list = scholarships_list.filter(min_gpa__gte=min_gpa_value)
        except (ValueError, TypeError):
            # Handle case where GPA is not a valid number
            pass

    if major and major != "All":
        scholarships_list = scholarships_list.filter(major=major)

    # Apply sorting
    if sort_by == 'newest':
        scholarships_list = scholarships_list.order_by('-created_at')
    else:  # This handles 'deadline' sort_by
        # Sorts by 'active' status first (0 for active, 1 for expired), then by deadline
        scholarships_list = scholarships_list.order_by(
            Case(
                When(deadline__gte=date.today(), then=0),
                default=1,
                output_field=IntegerField(),
            ),
            'deadline'
        )

    # --- Pagination Logic ---
    paginator = Paginator(scholarships_list, 2) # Show 10 scholarships per page
    page_number = request.GET.get('page')
    try:
        scholarships = paginator.page(page_number)
    except PageNotAnInteger:
        scholarships = paginator.page(1)
    except EmptyPage:
        scholarships = paginator.page(paginator.num_pages)

    context = {
        'scholarships': scholarships,
        'search_query': search_query,
        'selected_deadline': selected_deadline,
        'min_gpa_query': min_gpa_query,
        'selected_level': selected_level,
        'major': major,
        'sort_by': sort_by,
        'academic_level_choices': ACADEMIC_LEVEL_CHOICES,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'today': date.today(),
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

    context = {'form': form, 'page_title': 'Register for UCSYers Hub'}
    return render(request, 'registration/register.html', context)


@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role_selected_in_form = request.POST.get('role')
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'userprofile'):
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
                messages.error(request, f"Your account is registered as {user_actual_role}, but you selected {role_selected_in_form}.")
        else:
            messages.error(request, "Invalid username or password.")

    role_choices = UserProfile.ROLE_CHOICES
    return render(request, 'registration/login.html', {'role_choices': role_choices})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('home')



class InternshipsView(TemplateView):
    template_name = 'internships.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        context['testimonials'] = Testimonial.objects.all()
        return context

@login_required
def scholarship_detail(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    context = {
        'scholarship': scholarship,
        'today': date.today()
    }
    return render(request, 'scholarships/scholarship_detail.html', context)


# ---------- Student Dashboard & Wishlist ----------


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # Add this import


@login_required
def student_dashboard(request):
    user = request.user
    profile = user.userprofile
    wishlist_scholarships_list = user.wishlist.all().order_by('-id')  # Fetch all scholarships and order them

    paginator = Paginator(wishlist_scholarships_list, 2)  # Show 5 scholarships per page
    page = request.GET.get('page', 1)

    try:
        wishlist_scholarships = paginator.page(page)
    except PageNotAnInteger:
        wishlist_scholarships = paginator.page(1)
    except EmptyPage:
        wishlist_scholarships = paginator.page(paginator.num_pages)

    password_form = CustomPasswordChangeForm(user=user)
    profile_form = StudentProfileForm(instance=profile)

    if request.method == 'POST' and 'form_type' in request.POST:
        form_type = request.POST['form_type']

        if form_type == 'password_change':
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully!")
                return redirect('scholarships:student_dashboard')
        elif form_type == 'profile_update':
            profile_form = StudentProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('scholarships:student_dashboard')

    context = {
        'user': user,
        'wishlist_scholarships': wishlist_scholarships,  # Pass the paginated object
        'password_form': password_form,
        'profile_form': profile_form,
        'today': date.today(),
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def toggle_wishlist(request, scholarship_id):
    scholarship = get_object_or_404(Scholarship, id=scholarship_id)
    user = request.user
    if user.wishlist.filter(id=scholarship_id).exists():
        user.wishlist.remove(scholarship)
        action = 'removed'
    else:
        user.wishlist.add(scholarship)
        action = 'added'
    return JsonResponse({'status': 'success', 'action': action, 'wishlist_count': user.wishlist.count()})


@require_POST
@login_required
def remove_from_wishlist(request, scholarship_id):
    try:
        scholarship = Scholarship.objects.get(id=scholarship_id)
        request.user.wishlist.remove(scholarship)
        return JsonResponse({'success': True, 'wishlist_count': request.user.wishlist.count()})
    except Scholarship.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Scholarship not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Announcement
# ---------- Announcements ----------
@login_required(login_url='login')


def announcements_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    today = timezone.now()

    # Mark recent announcements
    for ann in announcements:
        ann.is_new = (today - ann.created_at).days < 7

    paginator = Paginator(announcements, 6)  # 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Announcements',
        'page_obj': page_obj
    }
    return render(request, 'announcements_list.html', context)

def resources(request):
    return render(request, 'resources.html')