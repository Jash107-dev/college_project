from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Count, Avg, Max, Min
import csv

from .models import Employee, Leave
from .forms import EmployeeForm, EmployeeStatusForm, LeaveForm


# ---- permission helper ----

def admin_required(view_func):
    # decorator that blocks non-admin users from accessing admin views
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('employee_self_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ---- admin views ----

@admin_required
def dashboard(request):
    total    = Employee.objects.count()
    active   = Employee.objects.filter(status='Active').count()
    inactive = Employee.objects.filter(status='Inactive').count()
    on_leave = Employee.objects.filter(status='On Leave').count()

    avg_salary = Employee.objects.aggregate(avg=Avg('salary'))['avg'] or 0
    max_salary = Employee.objects.aggregate(max=Max('salary'))['max'] or 0
    min_salary = Employee.objects.aggregate(min=Min('salary'))['min'] or 0

    dept_data        = Employee.objects.values('department').annotate(count=Count('id')).order_by('-count')
    gender_data      = Employee.objects.values('gender').annotate(count=Count('id'))
    recent_employees = Employee.objects.order_by('-id')[:5]
    pending_leaves   = Leave.objects.filter(status='Pending').count()

    context = {
        'total': total, 'active': active, 'inactive': inactive, 'on_leave': on_leave,
        'avg_salary': int(avg_salary), 'max_salary': max_salary, 'min_salary': min_salary,
        'dept_data': dept_data, 'gender_data': gender_data,
        'recent_employees': recent_employees, 'pending_leaves': pending_leaves,
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
        employees = (employees.filter(name__icontains=search) |
                     employees.filter(email__icontains=search) |
                     employees.filter(employee_id__icontains=search))
    if department:
        employees = employees.filter(department=department)
    if status:
        employees = employees.filter(status=status)
    if gender:
        employees = employees.filter(gender=gender)

    total = employees.count()
    paginator = Paginator(employees, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj, 'search': search, 'department': department,
        'status': status, 'gender': gender, 'total': total,
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
        messages.success(request, f'{emp.name} added. Login: {emp.user.username} | Password: {emp._generate_password()}')
        return redirect('employee_list')
    return render(request, 'employee/add_employee.html', {'form': form})


@admin_required
def edit_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    form = EmployeeForm(request.POST or None, instance=emp)
    if request.method == 'POST' and form.is_valid():
        emp = form.save()
        messages.success(request, f'{emp.name} has been updated successfully.')
        return redirect('employee_list')
    return render(request, 'employee/edit_employee.html', {'form': form, 'emp': emp})


@admin_required
def delete_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        name = emp.name
        if emp.user:
            emp.user.delete()
        else:
            emp.delete()
        messages.success(request, f'{name} has been deleted.')
        return redirect('employee_list')
    return render(request, 'employee/delete_employee.html', {'emp': emp})


@admin_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Name', 'Email', 'Phone', 'Gender',
                     'Department', 'Designation', 'Salary', 'Date of Joining', 'Status'])
    for emp in Employee.objects.all().order_by('employee_id'):
        writer.writerow([emp.employee_id, emp.name, emp.email, emp.phone or '',
                         emp.gender, emp.department or '', emp.designation or '',
                         emp.salary, emp.date_of_joining or '', emp.status])
    return response


# ---- employee self-service views ----

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


# ---- leave management views ----

@login_required
def apply_leave(request):
    # admin/superuser should NOT apply leave - they only manage it
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, 'Admins cannot apply for leave. Use the Leave Requests panel to manage employee leaves.')
        return redirect('admin_leave_list')

    form = LeaveForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.employee = request.user
        leave.status   = 'Pending'
        leave.save()
        messages.success(request, 'Leave application submitted successfully.')
        return redirect('my_leaves')
    return render(request, 'leave/apply_leave.html', {'form': form})


@login_required
def my_leaves(request):
    # employee sees only their own leave history
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_leave_list')
    leaves = Leave.objects.filter(employee=request.user)
    return render(request, 'leave/my_leaves.html', {'leaves': leaves})


@admin_required
def admin_leave_list(request):
    # admin sees all leave requests with optional status filter
    status_filter = request.GET.get('status', '')
    leaves = Leave.objects.select_related('employee').all()
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    # counts for the summary badges
    pending_count  = Leave.objects.filter(status='Pending').count()
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

        # auto-update the linked employee's status to "On Leave"
        try:
            emp = leave.employee.employee_profile
            emp.status = 'On Leave'
            emp.save()
        except Employee.DoesNotExist:
            pass  # user has no employee record, skip silently

        messages.success(request, f'Leave approved for {leave.employee.get_full_name() or leave.employee.username}. Employee status updated to On Leave.')
    return redirect('admin_leave_list')


@admin_required
def reject_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    if leave.status == 'Pending':
        leave.status = 'Rejected'
        leave.save()

        # if employee was set to On Leave due to this request, revert them to Active
        # only revert if they have no other approved leaves still active
        try:
            emp = leave.employee.employee_profile
            has_other_approved = Leave.objects.filter(
                employee=leave.employee,
                status='Approved'
            ).exclude(id=leave.id).exists()

            if not has_other_approved and emp.status == 'On Leave':
                emp.status = 'Active'
                emp.save()
        except Employee.DoesNotExist:
            pass

        messages.error(request, f'Leave rejected for {leave.employee.get_full_name() or leave.employee.username}.')
    return redirect('admin_leave_list')
