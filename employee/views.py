
from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})


def add_employee(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        salary = request.POST.get('salary')

        Employee.objects.create(
            name=name,
            email=email,
            department=department,
            salary=salary
        )
        return redirect('employee_list')

    return render(request, 'add_employee.html')

def edit_employee(request, id):
    emp = get_object_or_404(Employee, id=id)

    if request.method == "POST":
        emp.name = request.POST['name']
        emp.email = request.POST['email']
        emp.department = request.POST['department']
        emp.salary = request.POST['salary']
        emp.save()
        return redirect('employee_list')

    return render(request, 'edit_employee.html', {'emp': emp})


def delete_employee(request, id):
    emp = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        emp.delete()
        return redirect('employee_list')
    return render(request, 'delete_employee.html', {'emp': emp})