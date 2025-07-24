from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view, custom_login
from scholarships.views import home_view  #
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # App-specific URLs
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
     path('register/', register_view, name='register'), 

    path('accounts/', include('django.contrib.auth.urls')),

   
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
