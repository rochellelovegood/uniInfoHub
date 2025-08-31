# uniHub/uniHub/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view, custom_login, logout_view, InternshipsView,scholarship_detail,student_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    # URL for the custom login view
    path('login/', custom_login, name='login'),
    
    # All scholarship-related URLs are now handled by the scholarships app's urls.py
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
    
    # URL for the custom registration view
    path('register/', register_view, name='register'),
    
    # URLs for the faculties app
    path('faculties/', include('faculties.urls', namespace='faculties')),
    
    # URL for the custom logout view
    path('logout/', logout_view, name='logout'),
    
    # URL for the internships view
    path('internships/', InternshipsView.as_view(), name='internships'),

    path('student_dashboard/', student_dashboard, name='student_dashboard'),
    
    


]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)