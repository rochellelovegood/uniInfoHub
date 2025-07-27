from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
<<<<<<< HEAD
from scholarships.views import home_view, register_view, homepage
=======
from scholarships.views import home_view, register_view, custom_login
>>>>>>> main
from scholarships.views import home_view  #
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # App-specific URLs
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
<<<<<<< HEAD
     path('register/', register_view, name='register'), 
    path('homepage/', homepage,name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),

=======
    path('register/', register_view, name='register'),
    path('login/',custom_login,name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
>>>>>>> main
]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
