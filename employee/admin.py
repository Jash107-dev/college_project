from django.contrib import admin
from .models import Employee, Leave

admin.site.register(Employee)

# register Leave so admin can manage it from the django admin panel too
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display  = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on']
    list_filter   = ['status', 'leave_type']
    search_fields = ['employee__username', 'employee__first_name']
