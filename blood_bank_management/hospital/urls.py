from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('', views.hospital_user_login, name='login'),
    path('signup/', views.hospital_user_signup, name='signup'),
    path('logout/', views.hospital_logout, name='logout'),
    path('<int:hospital_id>/hospital_list/', views.hospital_list, name='hospital_list'),
    path('<int:hospital_id>/inventory/', views.manage_inventory, name='manage_inventory'),
    path('<int:hospital_id>/requests/', views.manage_requests, name='manage_requests'),
    path('<int:hospital_id>/donate_blood/', views.donate_blood, name='donate_blood'),
    path('<int:hospital_id>/requests/', views.manage_requests, name='manage_requests'),
    path('request_blood/', views.request_blood, name='request_blood'),
    path('request_history/', views.request_history, name='request_history'), 
]
