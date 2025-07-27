# uniHub/scholarships/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
<<<<<<< HEAD
from scholarships.views import home_view, register_view, homepage
=======
from scholarships.views import home_view, register_view, custom_login
>>>>>>> main
from django.urls import path
from . import views

app_name = 'scholarships' # This helps in namespacing URLs (e.g., 'scholarships:list')

urlpatterns = [
    path('', views.scholarship_list, name='list'),
    path('register/', register_view, name='register'), # <--- ADD THIS LINE BACK HERE
<<<<<<< HEAD
    path('homepage/',views.homepage,name='homepage'),
    path('',views.scholarship_list,name='list')
=======
    path('login/',custom_login,name='login'),

>>>>>>> main
]