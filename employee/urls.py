from django.urls import path
from . import views

urlpatterns = [
    # Admin routes
    path('',views.dashboard,name='dashboard'),
    path('list/',views.employee_list,name='employee_list'),
    path('add/',views.add_employee,name='add_employee'),
    path('edit/<int:id>/',views.edit_employee,name='edit_employee'),
    path('delete/<int:id>/',views.delete_employee,name='delete_employee'),
    path('profile/<int:id>/',views.employee_profile,name='employee_profile'),
    path('export/',views.export_csv,name='export_csv'),

    # Employee routes 
    path('me/',views.employee_self_dashboard,name='employee_self_dashboard'),
    path('me/update-status/',views.employee_update_status,name='employee_update_status'),
]