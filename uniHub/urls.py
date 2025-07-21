from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the home view from the core app (recommended structure)
from scholarships.views import home_view  # If you're still using uniHub.views, adjust accordingly

# Optional: Custom error handlers (you'll need to define these vie
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # App-specific URLs
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),

    # Built-in Django auth views (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Future expansion (uncomment when apps are ready)
    # path('announcements/', include('announcements.urls', namespace='announcements')),
    # path('resources/', include('resources.urls', namespace='resources')),
    # path('users/', include('users.urls', namespace='users')),
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
