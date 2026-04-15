from django.db import models
from django.contrib.auth.models import User


# this is the main employee model
# it stores all the info about each employee in the company
class Employee(models.Model):

    # these are the choices for gender field
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # status of the employee - active means working, inactive means left
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ]

    # all the departments in our company
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

    # linking employee to django user so they can login
    # set_null means if user is deleted employee record stays
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
            # get the last employee and increment the number
            # if no employee exists start from 1
        last = Employee.objects.order_by('id').last()
        num  = int(last.employee_id.replace('EMP', '')) + 1 if last else 1
        return f'EMP{num:03d}'

    def _generate_password(self):
            # password is first 3 digits of phone + year of joining
            # eg phone=9876543210 joined=2023 then password=9872023
        phone_part = (self.phone or '')[:3]
        year_part  = str(self.date_of_joining.year) if self.date_of_joining else ''
        if phone_part and year_part:
            return f'{phone_part}{year_part}'
        return self.employee_id  # if phone or year not there use emp id as fallback

    def create_user_account(self):
            # this creates a django login account for the employee
            # so they can login to the portal using their emp id
        if self.user:
            return  # already has account no need to create again

        username = self.employee_id.lower()
        password = self._generate_password()

        # if username already taken add id at end to make it unique
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
            # overriding save to auto generate emp id and create user account
        is_new = not self.pk
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()
        super().save(*args, **kwargs)
        # only create user if its a new employee and no user linked yet
        if is_new and not self.user:
            self.create_user_account()

    def __str__(self):
        return f'{self.employee_id} - {self.name}'


# leave model - stores all leave requests made by employees
class Leave(models.Model):

    # types of leave an employee can apply for
    LEAVE_TYPE_CHOICES = [
        ('Sick',   'Sick Leave'),
        ('Casual', 'Casual Leave'),
        ('Paid',   'Paid Leave'),
    ]

    # status of the leave request
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # using user foreignkey instead of employee directly
    # this is easier bcoz leave is linked to login account
    employee   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date   = models.DateField()
    reason     = models.TextField()
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)  # auto fills when leave is submitted

    class Meta:
            # show newest leave requests first
        ordering = ['-applied_on']

    def __str__(self):
        return f'{self.employee.username} - {self.leave_type} ({self.status})'

    @property
    def total_days(self):
            # +1 bcoz both start and end date are included
            # eg 1st to 3rd = 3 days not 2
        return (self.end_date - self.start_date).days + 1
