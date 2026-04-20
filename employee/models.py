from django.db import models
from django.contrib.auth.models import User


# stores all employee info (main model)
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

    user            = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')  # if the user is deleted also the employee stays
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
        num  = int(last.employee_id.replace('EMP', '')) + 1 if last else 1  # increment from last or start at 1
        return f'EMP{num:03d}'

    def _generate_password(self):
        phone_part = (self.phone or '')[:3]  # first 3 digits of phone
        year_part  = str(self.date_of_joining.year) if self.date_of_joining else ''
        if phone_part and year_part:
            return f'{phone_part}{year_part}' 
        return self.employee_id  # fallback if phone or year missing

    def create_user_account(self):
        if self.user:
            return  # already has account skip
        username = self.employee_id.lower()
        password = self._generate_password()
        if User.objects.filter(username=username).exists():
            username = f'{username}_{self.id}'  # make unique if taken
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
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()  # auto generate before saving
        super().save(*args, **kwargs)
        if is_new and not self.user:
            self.create_user_account()  # create login account for new emp

    def __str__(self):
        return f'{self.employee_id} - {self.name}'


# leave model - one row per leave request
class Leave(models.Model):

    LEAVE_TYPE_CHOICES = [  # 3 types of leave
        ('Sick',   'Sick Leave'),
        ('Casual', 'Casual Leave'),
        ('Paid',   'Paid Leave'),
    ]

    STATUS_CHOICES = [  # starts as pending then admin changes it
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')  # linked to user not employee directly
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date   = models.DateField()
    reason     = models.TextField()
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)  # auto set on  create

    class Meta:
        ordering = ['-applied_on']  # recent newest will come first in the list

    def __str__(self):
        return f'{self.employee.username} - {self.leave_type} ({self.status})'

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1  #both current day and last day are included as a whole day so+1
