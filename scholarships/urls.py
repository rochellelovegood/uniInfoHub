# uniHub/scholarships/urls.py

# Remove unnecessary imports from here that should be in the project-level urls.py
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

from django.urls import path
from . import views
from scholarships.views import home_view, register_view, custom_login # <<< Ensure these are imported from views

app_name = 'scholarships' # This helps in namespacing URLs (e.g., 'scholarships:list')

urlpatterns = [
    path('', views.scholarship_list_view, name='list'), # Ensure this matches your view function name
    path('register/', register_view, name='register'),
    path('login/', custom_login, name='login'), # This is your custom login view
    # You will likely have more paths here based on our previous discussions, e.g.:
    # path('<int:pk>/', views.scholarship_detail_view, name='detail'),
    # path('post/', views.post_scholarship_view, name='post_scholarship'),
]