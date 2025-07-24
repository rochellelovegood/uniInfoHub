# uniHub/scholarships/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scholarships.views import home_view, register_view
from django.urls import path
from . import views

app_name = 'scholarships' # This helps in namespacing URLs (e.g., 'scholarships:list')

urlpatterns = [
    path('', views.scholarship_list, name='list'),
    
]