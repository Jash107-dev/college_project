from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from employee.models import Employee


@login_required
def home(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    return redirect('employee_self_dashboard')


def login_view(request):
    error      = None
    login_type = 'admin' 

    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'admin')

        # this is for admin login ,admins will use their username and password to log in, while employees will use their employee id and a password (which is linked to their user account).
        if login_type == 'admin':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Invalid username or password. Please try again.'

                         # employee login 
        elif login_type == 'employee':
            employee_id = request.POST.get('employee_id', '').strip().upper()
            password    = request.POST.get('emp_password', '')

                        #searching for the existing employee
            try:
                emp = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                error = 'No employee found with that ID. Please check and try again.'
                return render(request, 'accounts/login.html', {
                    'error': error, 'login_type': login_type
                })

                  #checking if the user has linked with the employee record
            if emp.user is None:
                error = 'Your account is not set up yet. Please contact your admin.'
                return render(request, 'accounts/login.html', {
                    'error': error, 'login_type': login_type
                })

                           #authenting the user that is linked to the employe list
            user = authenticate(request, username=emp.user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('employee_self_dashboard')
            else:
                error = 'Incorrect password. Hint: first 3 digits of phone + year of joining.'

    return render(request, 'accounts/login.html', {
        'error':      error,
        'login_type': login_type,
    })


def logout_view(request):
    logout(request)
    return redirect('login')