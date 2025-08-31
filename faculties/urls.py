# uniHub/faculty/urls.py
from django.urls import path
from . import views


app_name = 'faculties'

urlpatterns = [
    path('', views.faculty_dashboard_home, name='faculty_dashboard_home'),
    path('post/', views.post_scholarship, name='post_scholarship'),
    path('logout/', views.logout_view, name='logout'),
    
    path('edit/<int:scholarship_id>/', views.edit_scholarship, name='edit_scholarship'),
    path('delete/<int:scholarship_id>/', views.delete_scholarship, name='delete_scholarship'),
    path('post-company/', views.post_company, name='post_company'),
    path('company/delete/<int:pk>/', views.delete_company, name='delete_company'),
    path('post-announcement/', views.post_announcement, name='post_announcement'),
    path('edit-announcement/<int:pk>/', views.edit_announcement, name='edit_announcement'),
    path('delete-announcement/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
]