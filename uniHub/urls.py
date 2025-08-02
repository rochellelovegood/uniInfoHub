from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view, custom_login, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # URL for the custom login view
    path('login/', custom_login, name='login'),
    
    # All scholarship-related URLs are now handled by the scholarships app's urls.py
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
    
    path('register/', register_view, name='register'),
    
    # The 'post_scholarship' URL is now expected to be in scholarships/urls.py
    # path('post/', post_scholarship_view, name='post_scholarship'),  # <-- REMOVED

    path('faculties/', include('faculties.urls', namespace='faculties')), # Added a namespace for consistency
    path('logout/', logout_view, name='logout'),
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
