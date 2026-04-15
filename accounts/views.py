from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from employee.models import Employee


# home view - just redirects based on who is logged in
@login_required
def home(request):
        # if admin go to admin dashboard else go to employee dashboard
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    return redirect('employee_self_dashboard')


# login view - handles both admin and employee login
def login_view(request):
    error      = None
    login_type = 'admin'  # default is admin login

    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'admin')

        # admin login - uses username and password directly
        if login_type == 'admin':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Invalid username or password. Please try again.'

        # employee login - uses employee id and auto generated password
        elif login_type == 'employee':
            employee_id = request.POST.get('employee_id', '').strip().upper()
            password    = request.POST.get('emp_password', '')

            # first find the employee record using emp id
            try:
                emp = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                    # emp id not found in db
                error = 'No employee found with that ID. Please check and try again.'
                return render(request, 'accounts/login.html', {
                    'error': error, 'login_type': login_type
                })

            # check if employee has a user account linked
            # this is created automatically when emp is added
            if emp.user is None:
                    # this means admin didnt create user account for this emp
                error = 'Your account is not set up yet. Please contact your admin.'
                return render(request, 'accounts/login.html', {
                    'error': error, 'login_type': login_type
                })

            # now authenticate using the linked user account
            user = authenticate(request, username=emp.user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('employee_self_dashboard')
            else:
                    # wrong password - give hint about password format
                error = 'Incorrect password. Hint: first 3 digits of phone + year of joining.'

    return render(request, 'accounts/login.html', {
        'error':      error,
        'login_type': login_type,
    })


# logout - clears session and goes back to login page
def logout_view(request):
    logout(request)
    return redirect('login')
