from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_welcome_email(employee, password):
    """Send welcome email to new employee with login credentials"""
    subject = 'Welcome to Employee Management System'
    
    context = {
        'employee_name': employee.name,
        'employee_id': employee.employee_id,
        'username': employee.user.username,
        'password': password,
        'email': employee.email,
    }
    
    html_message = render_to_string('emails/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_leave_application_email(leave):
    """Notify admin when employee applies for leave"""
    subject = f'New Leave Application - {leave.employee.get_full_name() or leave.employee.username}'
    
    context = {
        'employee_name': leave.employee.get_full_name() or leave.employee.username,
        'leave_type': leave.get_leave_type_display(),
        'start_date': leave.start_date,
        'end_date': leave.end_date,
        'total_days': leave.total_days,
        'reason': leave.reason,
    }
    
    html_message = render_to_string('emails/leave_application.html', context)
    plain_message = strip_tags(html_message)
    
    # Get admin emails
    from django.contrib.auth.models import User
    admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
    admin_emails = [email for email in admin_emails if email]
    
    if not admin_emails:
        return False
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending leave application email: {e}")
        return False


def send_leave_status_email(leave, approved=True):
    """Notify employee when their leave is approved or rejected"""
    status = 'Approved' if approved else 'Rejected'
    subject = f'Leave Request {status}'
    
    # Get employee email
    try:
        employee_profile = leave.employee.employee_profile
        employee_email = employee_profile.email
    except:
        return False
    
    context = {
        'employee_name': leave.employee.get_full_name() or leave.employee.username,
        'leave_type': leave.get_leave_type_display(),
        'start_date': leave.start_date,
        'end_date': leave.end_date,
        'total_days': leave.total_days,
        'status': status,
        'approved': approved,
    }
    
    html_message = render_to_string('emails/leave_status.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending leave status email: {e}")
        return False


def send_employee_update_notification(employee, updated_by):
    """Notify employee when their profile is updated"""
    subject = 'Your Profile Has Been Updated'
    
    context = {
        'employee_name': employee.name,
        'updated_by': updated_by.get_full_name() or updated_by.username,
    }
    
    html_message = render_to_string('emails/profile_updated.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending profile update email: {e}")
        return False
