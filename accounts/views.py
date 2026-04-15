from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from employee.models import Employee


# redirects to correct dashboard based on user type
@login_required
def home(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')  # admin goes here
    return redirect('employee_self_dashboard')  # employee goes here


# handles both admin and employee login in one view
def login_view(request):
    error      = None
    login_type = 'admin'  # default tab is admin

    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'admin')

        if login_type == 'admin':  # admin uses username + password
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user     = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Invalid username or password. Please try again.'

        elif login_type == 'employee':  # employee uses emp id + auto password
            employee_id = request.POST.get('employee_id', '').strip().upper()
            password    = request.POST.get('emp_password', '')
            try:
                emp = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                error = 'No employee found with that ID. Please check and try again.'
                return render(request, 'accounts/login.html', {'error': error, 'login_type': login_type})
            if emp.user is None:  # user account not created yet
                error = 'Your account is not set up yet. Please contact your admin.'
                return render(request, 'accounts/login.html', {'error': error, 'login_type': login_type})
            user = authenticate(request, username=emp.user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('employee_self_dashboard')
            else:
                error = 'Incorrect password. Hint: first 3 digits of phone + year of joining.'

    return render(request, 'accounts/login.html', {'error': error, 'login_type': login_type})


# clears session and sends back to login
def logout_view(request):
    logout(request)
    return redirect('login')
