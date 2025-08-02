# uniHub/uniHub/urls.py

from django.contrib import admin
from django.urls import path, include
from scholarships.views import home_view # Import your homepage view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The Django admin panel
    path('admin/', admin.site.urls),
    
    # This is the main project homepage
    path('', home_view, name='home'),
    
    # Include the URLs from the 'scholarships' app
    path('scholarships/', include('scholarships.urls')),

    # Include the URLs from the 'faculty' app
    # This path will be the base for all faculty URLs.
    # The dashboard will be accessible at /faculty/dashboard/
    path('faculty/', include('faculty.urls')),

    # Use Django's built-in logout view for simplicity and best practice
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

