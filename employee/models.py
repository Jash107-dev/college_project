from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ]

    DEPARTMENT_CHOICES = [
        ('HR', 'HR'),
        ('IT', 'IT'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
        ('Operations', 'Operations'),
        ('Sales', 'Sales'),
        ('Legal', 'Legal'),
        ('Admin', 'Admin'),
    ]

    user            = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    employee_id     = models.CharField(max_length=20, unique=True, blank=True)
    name            = models.CharField(max_length=100)
    email           = models.EmailField(unique=True)
    phone           = models.CharField(max_length=15, unique=True, blank=True, null=True)
    gender          = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    department      = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    designation     = models.CharField(max_length=100, blank=True, null=True)
    salary          = models.IntegerField(default=0)
    date_of_joining = models.DateField(blank=True, null=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def _generate_employee_id(self):
        last = Employee.objects.order_by('id').last()
        num  = int(last.employee_id.replace('EMP', '')) + 1 if last else 1
        return f'EMP{num:03d}'

    def _generate_password(self):
       
        phone_part  = (self.phone or '')[:3]
        year_part   = str(self.date_of_joining.year) if self.date_of_joining else ''
        if phone_part and year_part:
            return f'{phone_part}{year_part}'
        return self.employee_id  # fallback

    def create_user_account(self):
        #Create a Django User account for this employee.
        if self.user:
            return  # already has an account

        username = self.employee_id.lower()  # e.g. 'emp001'
        password = self._generate_password()

        # Make username unique if it already exists
        if User.objects.filter(username=username).exists():
            username = f'{username}_{self.id}'

        user = User.objects.create_user(
            username=username,
            email=self.email,
            password=password,
            first_name=self.name.split()[0],
            last_name=' '.join(self.name.split()[1:]) if len(self.name.split()) > 1 else '',
        )
        self.user = user
        Employee.objects.filter(pk=self.pk).update(user=user)

    def save(self, *args, **kwargs):
        is_new = not self.pk

        # Auto-generate employee_id for new employees
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()

        super().save(*args, **kwargs)

        # Auto-create user account after first save (so employee_id exists)
        if is_new and not self.user:
            self.create_user_account()

    def __str__(self):
        return f'{self.employee_id} - {self.name}'
    