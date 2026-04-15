from django.urls import path
from . import views

urlpatterns = [
    # admin - employee management
    path('', views.dashboard, name='dashboard'),
    path('list/', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add_employee'),
    path('edit/<int:id>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:id>/', views.delete_employee, name='delete_employee'),
    path('profile/<int:id>/', views.employee_profile, name='employee_profile'),
    path('export/', views.export_csv, name='export_csv'),

    # employee self service
    path('me/', views.employee_self_dashboard, name='employee_self_dashboard'),
    path('me/update-status/', views.employee_update_status, name='employee_update_status'),

    # leave management
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/my/', views.my_leaves, name='my_leaves'),
    path('leave/all/', views.admin_leave_list, name='admin_leave_list'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
]
