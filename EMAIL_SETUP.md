# 📧 Email Configuration Guide

## Overview
This project now includes email functionality for:
- Welcome emails when employees are added
- Leave application notifications to admins
- Leave approval/rejection notifications to employees
- Profile update notifications

## Setup Instructions

### 1. Gmail Setup (Recommended for Development)

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

#### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "Employee Management System"
4. Click "Generate"
5. Copy the 16-character password

### 2. Environment Variables Setup

#### Option A: Using Environment Variables (Recommended for Production)

**Windows (PowerShell):**
```powershell
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-app-password"
$env:DEFAULT_FROM_EMAIL="your-email@gmail.com"
```

**Linux/Mac:**
```bash
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"
export DEFAULT_FROM_EMAIL="your-email@gmail.com"
```

#### Option B: Using .env File (Development)

1. Install python-decouple:
```bash
pip install python-decouple
```

2. Create `.env` file in project root:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

3. Update `settings.py`:
```python
from decouple import config

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
```

### 3. Testing Email Configuration

Run this command to test email sending:
```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from Employee Management System.',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

If successful, you'll see: `1`

### 4. Alternative Email Providers

#### SendGrid
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

#### Outlook/Office 365
```python
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@outlook.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

#### AWS SES
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

## Email Features

### 1. Welcome Email
**Triggered:** When admin adds a new employee
**Recipient:** New employee
**Contains:**
- Employee ID
- Username
- Password
- Welcome message

### 2. Leave Application Email
**Triggered:** When employee applies for leave
**Recipient:** All admin users
**Contains:**
- Employee name
- Leave type
- Start and end dates
- Total days
- Reason

### 3. Leave Status Email
**Triggered:** When admin approves/rejects leave
**Recipient:** Employee who applied
**Contains:**
- Leave details
- Approval/rejection status
- Appropriate message

### 4. Profile Update Email
**Triggered:** When admin updates employee profile
**Recipient:** Updated employee
**Contains:**
- Notification of update
- Who made the update

## Troubleshooting

### Email Not Sending

1. **Check credentials:**
   - Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
   - Ensure you're using App Password, not regular password

2. **Check Gmail settings:**
   - 2FA must be enabled
   - App Password must be generated
   - "Less secure app access" is NOT needed with App Password

3. **Check firewall:**
   - Port 587 must be open
   - Try port 465 with EMAIL_USE_SSL=True

4. **Check console for errors:**
   - Look for authentication errors
   - Check for connection timeouts

### Common Errors

**SMTPAuthenticationError:**
- Wrong email or password
- Need to use App Password instead of regular password

**SMTPServerDisconnected:**
- Port blocked by firewall
- Try different port (465 with SSL)

**Connection timeout:**
- Check internet connection
- Verify EMAIL_HOST is correct
- Try different email provider

## Development Mode

For development without actual email sending, use console backend:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Emails will be printed to console instead of sent.

## Production Considerations

1. **Use environment variables** - Never commit credentials
2. **Use dedicated email service** - SendGrid, AWS SES, Mailgun
3. **Set up SPF/DKIM records** - Improve deliverability
4. **Monitor email quota** - Track sending limits
5. **Handle failures gracefully** - Log errors, retry failed sends
6. **Use email templates** - Maintain consistent branding

## Security Best Practices

✅ Never commit email credentials to git
✅ Use App Passwords, not account passwords
✅ Rotate credentials regularly
✅ Use environment variables
✅ Enable 2FA on email account
✅ Monitor for suspicious activity
✅ Use dedicated email for system notifications

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all environment variables are set
3. Test with console backend first
4. Check Django logs for detailed errors
