# uniHub/scholarships/urls.py
from django.urls import path
from . import views

# This is the standard way to define the app's name for Django's `reverse` function.
app_name = 'scholarships'

urlpatterns = [
    # Public-facing views for scholarships
    path('', views.scholarship_list_view, name='list'),

    # User authentication-related views
    path('register/', views.register_view, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:pk>/', views.scholarship_detail, name='scholarship_detail'),
    path('homepage/', views.homepage, name='homepage'),
]
