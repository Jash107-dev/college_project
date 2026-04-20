from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Count, Avg, Max, Min
import csv

from .models import Employee, Leave
from .forms import EmployeeForm, EmployeeStatusForm, LeaveForm
from .email_utils import (
    send_welcome_email,
    send_leave_application_email,
    send_leave_status_email,
    send_employee_update_notification
)


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        user_is_staff = request.user.is_staff
        user_is_superuser = request.user.is_superuser
        
        if not user_is_staff and not user_is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('employee_self_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    total = Employee.objects.count()
    active = Employee.objects.filter(status='Active').count()
    inactive = Employee.objects.filter(status='Inactive').count()
    on_leave = Employee.objects.filter(status='On Leave').count()
    
    salary_stats = Employee.objects.aggregate(
        avg=Avg('salary'),
        max=Max('salary'),
        min=Min('salary')
    )
    avg_salary = salary_stats['avg'] or 0
    max_salary = salary_stats['max'] or 0
    min_salary = salary_stats['min'] or 0
    
    dept_data = Employee.objects.values('department').annotate(count=Count('id')).order_by('-count')
    gender_data = Employee.objects.values('gender').annotate(count=Count('id'))
    recent_employees = Employee.objects.order_by('-id')[:5]
    pending_leaves = Leave.objects.filter(status='Pending').count()
    
    context = {
        'total': total,
        'active': active,
        'inactive': inactive,
        'on_leave': on_leave,
        'avg_salary': int(avg_salary),
        'max_salary': max_salary,
        'min_salary': min_salary,
        'dept_data': dept_data,
        'gender_data': gender_data,
        'recent_employees': recent_employees,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'employee/dashboard.html', context)


@admin_required
def employee_list(request):
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')
    status = request.GET.get('status', '')
    gender = request.GET.get('gender', '')
    
    employees = Employee.objects.all().order_by('-id')
    
    if search:
        name_matches = employees.filter(name__icontains=search)
        email_matches = employees.filter(email__icontains=search)
        id_matches = employees.filter(employee_id__icontains=search)
        employees = name_matches | email_matches | id_matches
    
    if department:
        employees = employees.filter(department=department)
    if status:
        employees = employees.filter(status=status)
    if gender:
        employees = employees.filter(gender=gender)
    
    total = employees.count()
    paginator = Paginator(employees, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'department': department,
        'status': status,
        'gender': gender,
        'total': total,
        'dept_choices': Employee.DEPARTMENT_CHOICES,
        'status_choices': Employee.STATUS_CHOICES,
        'gender_choices': Employee.GENDER_CHOICES,
    }
    return render(request, 'employee/employee_list.html', context)


@admin_required
def employee_profile(request, id):
    emp = get_object_or_404(Employee, id=id)
    return render(request, 'employee/employee_profile.html', {'emp': emp})


@admin_required
def add_employee(request):
    form = EmployeeForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        emp = form.save()
        password = emp._generate_password()
        success_msg = f'{emp.name} added. Login: {emp.user.username} | Password: {password}'
        messages.success(request, success_msg)
        
        # Send welcome email
        if send_welcome_email(emp, password):
            messages.info(request, f'Welcome email sent to {emp.email}')
        else:
            messages.warning(request, 'Employee added but email could not be sent.')
        
        return redirect('employee_list')
    
    return render(request, 'employee/add_employee.html', {'form': form})


@admin_required
def edit_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    form = EmployeeForm(request.POST or None, instance=emp)
    
    if request.method == 'POST' and form.is_valid():
        emp = form.save()
        messages.success(request, f'{emp.name} has been updated successfully.')
        
        # Send update notification email
        if send_employee_update_notification(emp, request.user):
            messages.info(request, f'Update notification sent to {emp.email}')
        
        return redirect('employee_list')
    
    return render(request, 'employee/edit_employee.html', {'form': form, 'emp': emp})


@admin_required
def delete_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        name = emp.name
        user = emp.user
        emp.delete()
        
        if user:
            user.delete()
        
        messages.success(request, f'{name} has been deleted successfully.')
        return redirect('employee_list')
    
    return render(request, 'employee/delete_employee.html', {'emp': emp})


@admin_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    headers = ['Employee ID', 'Name', 'Email', 'Phone', 'Gender', 'Department', 'Designation', 'Salary', 'Date of Joining', 'Status']
    writer.writerow(headers)
    
    all_employees = Employee.objects.all().order_by('employee_id')
    for emp in all_employees:
        row = [
            emp.employee_id,
            emp.name,
            emp.email,
            emp.phone or '',
            emp.gender,
            emp.department or '',
            emp.designation or '',
            emp.salary,
            emp.date_of_joining or '',
            emp.status
        ]
        writer.writerow(row)
    
    return response


@login_required
def employee_self_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    
    try:
        emp = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No employee record linked to your account.')
        return redirect('logout')
    
    return render(request, 'employee/self_dashboard.html', {'emp': emp})


@login_required
def employee_update_status(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    
    try:
        emp = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No employee record found.')
        return redirect('logout')
    
    form = EmployeeStatusForm(request.POST or None, instance=emp)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your status has been updated.')
        return redirect('employee_self_dashboard')
    
    return render(request, 'employee/self_update_status.html', {'form': form, 'emp': emp})


@login_required
def apply_leave(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, 'Admins cannot apply for leave. Use the Leave Requests panel to manage employee leaves.')
        return redirect('admin_leave_list')
    
    form = LeaveForm(request.POST or None, user=request.user)
    
    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.employee = request.user
        leave.status = 'Pending'
        leave.save()
        
        messages.success(request, 'Leave application submitted successfully.')
        
        # Send notification to admin
        if send_leave_application_email(leave):
            messages.info(request, 'Admin has been notified via email.')
        
        return redirect('my_leaves')
    
    return render(request, 'leave/apply_leave.html', {'form': form})


@login_required
def my_leaves(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_leave_list')
    
    leaves = Leave.objects.filter(employee=request.user)
    return render(request, 'leave/my_leaves.html', {'leaves': leaves})


@admin_required
def admin_leave_list(request):
    status_filter = request.GET.get('status', '')
    leaves = Leave.objects.select_related('employee').all()
    
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    
    pending_count = Leave.objects.filter(status='Pending').count()
    approved_count = Leave.objects.filter(status='Approved').count()
    rejected_count = Leave.objects.filter(status='Rejected').count()
    
    context = {
        'leaves': leaves,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'leave/admin_leave_list.html', context)


@admin_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    if leave.status == 'Pending':
        leave.status = 'Approved'
        leave.save()
        
        updated = Employee.objects.filter(user=leave.employee).update(status='On Leave')
        employee_name = leave.employee.get_full_name() or leave.employee.username
        
        if updated:
            messages.success(request, f'Leave approved for {employee_name}. Status updated to On Leave.')
        else:
            messages.success(request, f'Leave approved for {employee_name}.')
        
        # Send approval email to employee
        if send_leave_status_email(leave, approved=True):
            messages.info(request, f'Approval email sent to {employee_name}')
    
    return redirect('admin_leave_list')


@admin_required
def reject_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    if leave.status == 'Pending':
        leave.status = 'Rejected'
        leave.save()
        
        other_approved_leaves = Leave.objects.filter(
            employee=leave.employee,
            status='Approved'
        ).exclude(id=leave.id)
        
        has_other_approved = other_approved_leaves.exists()
        
        # change back to active only if no other approved leaves
        if not has_other_approved:
            Employee.objects.filter(user=leave.employee, status='On Leave').update(status='Active')
        
        employee_name = leave.employee.get_full_name() or leave.employee.username
        messages.error(request, f'Leave rejected for {employee_name}.')
        
        # Send rejection email to employee
        if send_leave_status_email(leave, approved=False):
            messages.info(request, f'Rejection email sent to {employee_name}')
    
    return redirect('admin_leave_list')
