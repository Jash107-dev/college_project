from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Count, Avg, Max, Min
import csv

from .models import Employee
from .forms import EmployeeForm, EmployeeStatusForm


 

def admin_required(view_func):#decoraters.
    
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('employee_self_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


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

    context = {
        'total':            total,
        'active':           active,
        'inactive':         inactive,
        'on_leave':         on_leave,
        'avg_salary':       int(avg_salary),
        'max_salary':       max_salary,
        'min_salary':       min_salary,
        'dept_data':        dept_data,
        'gender_data':      gender_data,
        'recent_employees': recent_employees,
    }
    return render(request, 'employee/dashboard.html', context)


@admin_required#list of employees .
def employee_list(request):
    search     = request.GET.get('search', '')
    department = request.GET.get('department', '')
    status     = request.GET.get('status', '')
    gender     = request.GET.get('gender', '')

    employees = Employee.objects.all().order_by('-id')

    if search:
        employees = (
            employees.filter(name__icontains=search) |
            employees.filter(email__icontains=search) |
            employees.filter(employee_id__icontains=search)
        )
    if department:
        employees = employees.filter(department=department)
    if status:
        employees = employees.filter(status=status)
    if gender:
        employees = employees.filter(gender=gender)

    total     = employees.count()
    paginator = Paginator(employees, 8)
    page_obj  = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj':       page_obj,
        'search':         search,
        'department':     department,
        'status':         status,
        'gender':         gender,
        'total':          total,
        'dept_choices':   Employee.DEPARTMENT_CHOICES,
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
        # User account is auto-created inside Employee.save()
        messages.success(
            request,
            f'{emp.name} added. Login: {emp.user.username} | '
            f'Password: {emp._generate_password()}'
        )
        return redirect('employee_list')
    return render(request, 'employee/add_employee.html', {'form': form})


@admin_required
def edit_employee(request, id):
    emp  = get_object_or_404(Employee, id=id)
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
        # Deleting the Employee also deletes the linked User (CASCADE on User side)
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
        writer.writerow([
            emp.employee_id, emp.name, emp.email, emp.phone or '',
            emp.gender, emp.department or '', emp.designation or '',
            emp.salary, emp.date_of_joining or '', emp.status,
        ])

    return response



#  EMPLOYEE SELF-SERVICE VIEWS


@login_required
def employee_self_dashboard(request):
    
    #After login, check if user is staff , redirect to admin dashboard.
    #Otherwise show their own profile page.
    
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
    #Employee can only update their own status.
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
 