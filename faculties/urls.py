# uniHub/faculty/urls.py
from django.urls import path
from . import views

app_name = 'faculties'

urlpatterns = [
    path('', views.faculty_dashboard_home, name='faculty_dashboard_home'),
    path('post/', views.post_scholarship, name='post_scholarship'),
    path('logout/', views.logout_view, name='logout'),
    path('scholarship/', views.scholarship_list_view, name='scholarship_list'),
    path('edit/<int:scholarship_id>/', views.edit_scholarship, name='edit_scholarship'),
    path('delete/<int:scholarship_id>/', views.delete_scholarship, name='delete_scholarship'),
    path('post-company/', views.post_company, name='post_company'),
    path('company/delete/<int:pk>/', views.delete_company, name='delete_company'),
    path('post-announcement/', views.post_announcement, name='post_announcement'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/activate/', views.activate_user, name='activate_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/reset-password/', views.reset_password, name='reset_password'),

    
]

