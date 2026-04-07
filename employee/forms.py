import re
from django import forms
from django.utils import timezone
from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        exclude = ['employee_id', 'user']
        widgets = {
            'name':            forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter full name'}),
            'email':           forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter email address'}),
            'phone':           forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 6301986139'}),
            'gender':          forms.Select(attrs={'class': 'form-input'}),
            'department':      forms.Select(attrs={'class': 'form-input'}),
            'designation':     forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Software Engineer'}),
            'salary':          forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Enter salary', 'min': '0'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status':          forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_name(self):   #clean is used for self validation .
        name = self.cleaned_data.get('name', '').strip() 
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if len(name) > 100:
            raise forms.ValidationError("Name cannot exceed 100 characters.")
        if not re.match(r"^[A-Za-z\s.\-']+$", name):
            raise forms.ValidationError("Name can only contain letters, spaces, dots, hyphens, and apostrophes.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        qs = Employee.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An employee with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone
        phone = phone.strip()
        if not re.match(r'^[+]?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number (7-15 digits, may include +, spaces, or hyphens).")
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise forms.ValidationError("Phone number must have between 7 and 15 digits.")
        qs = Employee.objects.filter(phone=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An employee with this phone number already exists.")
        return phone

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary is None:
            raise forms.ValidationError("Salary is required.")
        if salary < 0:
            raise forms.ValidationError("Salary cannot be negative.")
        if salary > 10_000_000:
            raise forms.ValidationError("Salary seems too high. Please enter a realistic value (max ₹1,00,00,000).")
        return salary

    def clean_designation(self):
        designation = self.cleaned_data.get('designation', '')
        if not designation:
            return designation
        designation = designation.strip()
        if len(designation) < 2:
            raise forms.ValidationError("Designation must be at least 2 characters.")
        if len(designation) > 100:
            raise forms.ValidationError("Designation cannot exceed 100 characters.")
        if not re.match(r'^[A-Za-z0-9\s.\-/&]+$', designation):
            raise forms.ValidationError("Designation contains invalid characters.")
        return designation

    def clean_date_of_joining(self):
        doj = self.cleaned_data.get('date_of_joining')
        if not doj:
            return doj
        today = timezone.now().date()
        if doj > today:
            raise forms.ValidationError("Date of joining cannot be in the future.")
        if doj.year < 1900:
            raise forms.ValidationError("Date of joining seems too old. Please enter a valid date.")
        return doj

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        valid = [c[0] for c in Employee.GENDER_CHOICES]
        if gender not in valid:
            raise forms.ValidationError("Please select a valid gender.")
        return gender

    def clean_status(self):
        status = self.cleaned_data.get('status')
        valid = [c[0] for c in Employee.STATUS_CHOICES]
        if status not in valid:
            raise forms.ValidationError("Please select a valid status.")
        return status

    def clean_department(self):
        department = self.cleaned_data.get('department')
        if not department:
            return department
        valid = [c[0] for c in Employee.DEPARTMENT_CHOICES]
        if department not in valid:
            raise forms.ValidationError("Please select a valid department.")
        return department


#  Employee self-service: status update only

class EmployeeStatusForm(forms.ModelForm):
    
    #Limited form — employee can ONLY update their own status.
    #Nothing else is editable through this form.
    
    class Meta:
        model  = Employee
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        valid  = [c[0] for c in Employee.STATUS_CHOICES]
        if status not in valid:
            raise forms.ValidationError("Please select a valid status.")
        return status          
    
    