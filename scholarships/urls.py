from django.urls import path
from . import views
from scholarships.views import home_view, register_view, custom_login, post_scholarship_view # <<< Ensure these are imported from views
from django.urls import path, include

app_name = 'scholarships' 

urlpatterns = [
    path('', views.scholarship_list_view, name='list'), # Ensure this matches your view function name
    path('register/', register_view, name='register'),
    path('login/', custom_login, name='login'), 
    path('post/', post_scholarship_view, name='post_scholarship'),# This is your custom login view
    path('logout/', views.logout_view, name='logout')
]