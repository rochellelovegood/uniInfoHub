from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view, custom_login, post_scholarship_view  # Import views directly from scholarships.views
from scholarships.views import home_view  #
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # App-specific URLs
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
    path('register/', register_view, name='register'), 
    path('post/', post_scholarship_view, name='post_scholarship'),
    path('accounts/', include('django.contrib.auth.urls')),

   
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
