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
    
]

