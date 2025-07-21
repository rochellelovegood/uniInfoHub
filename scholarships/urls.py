# uniHub/scholarships/urls.py

from django.urls import path
from . import views

app_name = 'scholarships' # This helps in namespacing URLs (e.g., 'scholarships:list')

urlpatterns = [
    path('', views.scholarship_list, name='list'),
]