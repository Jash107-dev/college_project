import random
import time

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from employee.models import Employee


@login_required
def home(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    return redirect('employee_self_dashboard')


# ── Admin login (username + password, unchanged) ──────────────────────────────

def login_view(request):
    """Admin login page — username/password only."""
    error = None

    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password.'

    return render(request, 'accounts/login.html', {'error': error})


# ── Employee login — Step 1: enter Employee ID, receive OTP ──────────────────

def employee_login_view(request):
    """Step 1 – employee enters their Employee ID; OTP is sent to their email."""
    error = None

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip()

        # Debug: print what we received (remove after confirming)
        print(f"[OTP Login] Received employee_id: '{employee_id}' (len={len(employee_id)})")

        try:
            emp = Employee.objects.get(employee_id__iexact=employee_id)
            print(f"[OTP Login] Found employee: {emp.employee_id} - {emp.name}")
        except Employee.DoesNotExist:
            print(f"[OTP Login] No employee found for '{employee_id}'")
            # List all IDs to help debug
            all_ids = list(Employee.objects.values_list('employee_id', flat=True))
            print(f"[OTP Login] All employee IDs in DB: {all_ids}")
            error = 'No employee found with that ID.'
            return render(request, 'accounts/employee_login.html', {'error': error})

        if emp.user is None:
            error = 'Your account is not set up yet. Please contact your admin.'
            return render(request, 'accounts/employee_login.html', {'error': error})

        if not emp.email:
            error = 'No email address on file. Please contact your admin.'
            return render(request, 'accounts/employee_login.html', {'error': error})

        # Generate 6-digit OTP and store in session with a 10-min expiry
        otp = str(random.randint(100000, 999999))
        request.session['emp_otp']         = otp
        request.session['emp_otp_expires'] = time.time() + 600   # 10 minutes
        request.session['emp_user_id']     = emp.user.id
        request.session['emp_email_hint']  = emp.email[:3] + '***@' + emp.email.split('@')[-1]

        # Send OTP email
        try:
            send_mail(
                subject='Your Login OTP – Employee Management System',
                message=(
                    f'Hi {emp.name},\n\n'
                    f'Your one-time password (OTP) is: {otp}\n\n'
                    f'It is valid for 10 minutes. Do not share it with anyone.\n\n'
                    f'If you did not request this, please contact your admin.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[emp.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'OTP email error: {e}')
            error = 'Could not send OTP email. Please try again or contact admin.'
            return render(request, 'accounts/employee_login.html', {'error': error})

        return redirect('employee_otp_verify')

    return render(request, 'accounts/employee_login.html', {'error': error})


# ── Employee login — Step 2: verify OTP ──────────────────────────────────────

def employee_otp_verify_view(request):
    """Step 2 – employee enters the OTP received by email."""
    # Guard: must have gone through step 1 first
    if not request.session.get('emp_otp'):
        return redirect('employee_login')

    error = None
    email_hint = request.session.get('emp_email_hint', '')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        # Check expiry
        if time.time() > request.session.get('emp_otp_expires', 0):
            # Clear session keys
            for key in ('emp_otp', 'emp_otp_expires', 'emp_user_id', 'emp_email_hint'):
                request.session.pop(key, None)
            error = 'OTP has expired. Please request a new one.'
            return render(request, 'accounts/employee_otp.html', {'error': error, 'expired': True})

        if entered_otp == request.session['emp_otp']:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=request.session['emp_user_id'])
            except User.DoesNotExist:
                error = 'Session error. Please try again.'
                return render(request, 'accounts/employee_otp.html', {'error': error, 'email_hint': email_hint})

            # Clear OTP session data
            for key in ('emp_otp', 'emp_otp_expires', 'emp_user_id', 'emp_email_hint'):
                request.session.pop(key, None)

            # Log the user in (bypass password check — OTP is the auth)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('employee_self_dashboard')
        else:
            error = 'Incorrect OTP. Please check your email and try again.'

    return render(request, 'accounts/employee_otp.html', {'error': error, 'email_hint': email_hint})


def logout_view(request):
    logout(request)
    return redirect('login')
