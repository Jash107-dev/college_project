from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee


@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {'employees': employees})


@login_required
def add_employee(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        salary_str = (request.POST.get('salary', '0') or '0').strip()
        Employee.objects.create(
            name=name, email=email, department=department,
            salary=int(salary_str or '0')
        )
        return redirect('employee_list')
    return render(request, 'employee/add_employee.html')


@login_required
def edit_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        salary_str = (request.POST.get('salary', '0') or '0').strip()
        emp.name = request.POST['name']
        emp.email = request.POST['email']
        emp.department = request.POST['department']
        emp.salary = int(salary_str or '0')
        emp.save()
        return redirect('employee_list')
    return render(request, 'employee/edit_employee.html', {'emp': emp})


@login_required
def delete_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        emp.delete()
        return redirect('employee_list')
    return render(request, 'employee/delete_employee.html', {'emp': emp})