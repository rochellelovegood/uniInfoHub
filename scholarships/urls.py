# uniHub/scholarships/urls.py
from django.urls import path
from . import views

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

    # From student-dashboard branch
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('toggle-wishlist/<int:scholarship_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('remove/<int:scholarship_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # From main branch
    path('announcements/', views.announcements_list, name='announcements_list'),
    path('resources/', views.resources, name='resources'),
]