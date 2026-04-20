from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),                              # admin login
    path('employee-login/', views.employee_login_view, name='employee_login'),  # employee step 1
    path('employee-otp/', views.employee_otp_verify_view, name='employee_otp_verify'),  # employee step 2
    path('logout/', views.logout_view, name='logout'),
]
