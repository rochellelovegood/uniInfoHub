from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view, homepage,custom_login, InternshipsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Homepage

    # App-specific URLs
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
     path('register/', register_view, name='register'), 
    path('homepage/', homepage,name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register_view, name='register'),
    path('login/',custom_login,name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('internships/', InternshipsView.as_view(), name='internships'),

]

# Only serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
