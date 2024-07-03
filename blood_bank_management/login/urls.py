from django.urls import path
from .views import custom_user_login, custom_user_signup, user_logout, home

app_name = 'login'

urlpatterns = [
    path('', custom_user_login, name='login'),
    path('signup/', custom_user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('home/', home, name="home") 
]
    