from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Employee
from .forms import EmployeeForm


def make_employee_data(**overrides):
    data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '9876543210',
        'gender': 'Male',
        'department': 'IT',
        'designation': 'Software Engineer',
        'salary': 50000,
        'date_of_joining': '2023-01-15',
        'status': 'Active',
    }
    data.update(overrides)
    return data


def create_employee(**overrides):
    defaults = {
        'name': 'Test Employee',
        'email': 'test@example.com',
        'phone': '9876543210',
        'gender': 'Male',
        'department': 'IT',
        'designation': 'Developer',
        'salary': 40000,
        'date_of_joining': '2022-06-01',
        'status': 'Active',
    }
    defaults.update(overrides)
    return Employee.objects.create(**defaults)


class EmployeeModelTest(TestCase):

    def test_employee_id_auto_generated_first(self):
        """First employee should get EMP001."""
        emp = create_employee()
        self.assertEqual(emp.employee_id, 'EMP001')

    def test_employee_id_auto_generated_sequential(self):
        """Second employee should get EMP002."""
        create_employee(email='a@example.com')
        emp2 = create_employee(email='b@example.com')
        self.assertEqual(emp2.employee_id, 'EMP002')

    def test_employee_id_not_overwritten_on_update(self):
        """Editing an employee should NOT change their employee_id."""
        emp = create_employee()
        original_id = emp.employee_id
        emp.name = 'Updated Name'
        emp.save()
        emp.refresh_from_db()
        self.assertEqual(emp.employee_id, original_id)

    def test_str_representation(self):
        """__str__ should return 'EMP001 - Name'."""
        emp = create_employee(name='Alice')
        self.assertEqual(str(emp), 'EMP001 - Alice')

    def test_default_status_is_active(self):
        """Default status should be Active."""
        emp = Employee(name='Bob', email='bob@example.com')
        self.assertEqual(emp.status, 'Active')

    def test_default_gender_is_male(self):
        emp = Employee(name='Bob', email='bob@example.com')
        self.assertEqual(emp.gender, 'Male')

    def test_default_salary_is_zero(self):
        emp = Employee(name='Bob', email='bob@example.com')
        self.assertEqual(emp.salary, 0)

    def test_email_must_be_unique(self):
        """Two employees cannot share the same email."""
        create_employee(email='dup@example.com')
        with self.assertRaises(Exception):
            create_employee(email='dup@example.com')

    def test_employee_id_must_be_unique(self):
        """employee_id field has unique=True."""
        field = Employee._meta.get_field('employee_id')
        self.assertTrue(field.unique)

    def test_phone_is_optional(self):
        """Phone can be blank/null."""
        emp = create_employee(phone=None)
        self.assertIsNone(emp.phone)

    def test_department_is_optional(self):
        emp = create_employee(department=None)
        self.assertIsNone(emp.department)


class EmployeeFormValidationTest(TestCase):

    def test_valid_form(self):
        form = EmployeeForm(data=make_employee_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_name_required(self):
        form = EmployeeForm(data=make_employee_data(name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_too_short(self):
        form = EmployeeForm(data=make_employee_data(name='A'))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_too_long(self):
        form = EmployeeForm(data=make_employee_data(name='A' * 101))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_with_numbers_rejected(self):
        form = EmployeeForm(data=make_employee_data(name='John123'))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_with_special_chars_rejected(self):
        form = EmployeeForm(data=make_employee_data(name='John@Doe'))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_with_hyphen_allowed(self):
        form = EmployeeForm(data=make_employee_data(name='Mary-Jane'))
        self.assertTrue(form.is_valid(), form.errors)

    def test_name_with_dot_allowed(self):
        form = EmployeeForm(data=make_employee_data(name='A. Kumar'))
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_required(self):
        form = EmployeeForm(data=make_employee_data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email_format(self):
        form = EmployeeForm(data=make_employee_data(email='notanemail'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_email_without_domain(self):
        form = EmployeeForm(data=make_employee_data(email='user@'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email_rejected(self):
        """Cannot add two employees with the same email."""
        create_employee(email='dup@example.com')
        form = EmployeeForm(data=make_employee_data(email='dup@example.com'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_edit_own_email_allowed(self):
        """When editing, employee can keep their own email."""
        emp = create_employee(email='own@example.com')
        form = EmployeeForm(data=make_employee_data(email='own@example.com'), instance=emp)
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_stored_as_lowercase(self):
        form = EmployeeForm(data=make_employee_data(email='UPPER@EXAMPLE.COM'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'upper@example.com')

    def test_phone_optional(self):
        form = EmployeeForm(data=make_employee_data(phone=''))
        self.assertTrue(form.is_valid(), form.errors)

    def test_phone_with_letters_rejected(self):
        form = EmployeeForm(data=make_employee_data(phone='98765ABCDE'))
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_phone_too_short_rejected(self):
        form = EmployeeForm(data=make_employee_data(phone='123'))
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_phone_too_long_rejected(self):
        form = EmployeeForm(data=make_employee_data(phone='1' * 16))
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_phone_with_plus_allowed(self):
        form = EmployeeForm(data=make_employee_data(phone='+919876543210'))
        self.assertTrue(form.is_valid(), form.errors)

    def test_negative_salary_rejected(self):
        form = EmployeeForm(data=make_employee_data(salary=-1))
        self.assertFalse(form.is_valid())
        self.assertIn('salary', form.errors)

    def test_zero_salary_allowed(self):
        form = EmployeeForm(data=make_employee_data(salary=0))
        self.assertTrue(form.is_valid(), form.errors)

    def test_salary_above_limit_rejected(self):
        form = EmployeeForm(data=make_employee_data(salary=10_000_001))
        self.assertFalse(form.is_valid())
        self.assertIn('salary', form.errors)

    def test_salary_at_limit_allowed(self):
        form = EmployeeForm(data=make_employee_data(salary=10_000_000))
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_date_rejected(self):
        future = (timezone.now().date().replace(year=timezone.now().year + 1)).isoformat()
        form = EmployeeForm(data=make_employee_data(date_of_joining=future))
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_joining', form.errors)

    def test_today_date_allowed(self):
        today = timezone.now().date().isoformat()
        form = EmployeeForm(data=make_employee_data(date_of_joining=today))
        self.assertTrue(form.is_valid(), form.errors)

    def test_date_optional(self):
        form = EmployeeForm(data=make_employee_data(date_of_joining=''))
        self.assertTrue(form.is_valid(), form.errors)

    def test_very_old_date_rejected(self):
        form = EmployeeForm(data=make_employee_data(date_of_joining='1800-01-01'))
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_joining', form.errors)

    def test_invalid_gender_rejected(self):
        form = EmployeeForm(data=make_employee_data(gender='Unknown'))
        self.assertFalse(form.is_valid())
        self.assertIn('gender', form.errors)

    def test_invalid_status_rejected(self):
        form = EmployeeForm(data=make_employee_data(status='Retired'))
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_invalid_department_rejected(self):
        form = EmployeeForm(data=make_employee_data(department='Alien'))
        self.assertFalse(form.is_valid())
        self.assertIn('department', form.errors)

    def test_designation_with_special_chars_rejected(self):
        form = EmployeeForm(data=make_employee_data(designation='Dev@#$'))
        self.assertFalse(form.is_valid())
        self.assertIn('designation', form.errors)

    def test_designation_optional(self):
        form = EmployeeForm(data=make_employee_data(designation=''))
        self.assertTrue(form.is_valid(), form.errors)


class EmployeeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.emp = create_employee()

    def test_dashboard_requires_login(self):
        """Logged-out user should be redirected to login."""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/employee/')

    def test_employee_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 302)

    def test_add_employee_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('add_employee'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/dashboard.html')

    def test_dashboard_context_has_counts(self):
        response = self.client.get(reverse('dashboard'))
        self.assertIn('total', response.context)
        self.assertIn('active', response.context)
        self.assertIn('inactive', response.context)
        self.assertIn('on_leave', response.context)

    def test_dashboard_total_count_correct(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['total'], 1)

    def test_employee_list_loads(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_list.html')

    def test_employee_list_shows_employee(self):
        response = self.client.get(reverse('employee_list'))
        self.assertContains(response, self.emp.name)

    def test_search_by_name(self):
        create_employee(name='Unique Person', email='unique@example.com')
        response = self.client.get(reverse('employee_list'), {'search': 'Unique'})
        self.assertContains(response, 'Unique Person')
        self.assertNotContains(response, 'Test Employee')

    def test_search_by_email(self):
        response = self.client.get(reverse('employee_list'), {'search': 'test@example.com'})
        self.assertContains(response, self.emp.name)

    def test_filter_by_department(self):
        create_employee(name='HR Person', email='hr@example.com', department='HR')
        response = self.client.get(reverse('employee_list'), {'department': 'HR'})
        self.assertContains(response, 'HR Person')
        self.assertNotContains(response, 'Test Employee')

    def test_filter_by_status(self):
        create_employee(name='Inactive One', email='inactive@example.com', status='Inactive')
        response = self.client.get(reverse('employee_list'), {'status': 'Inactive'})
        self.assertContains(response, 'Inactive One')
        self.assertNotContains(response, 'Test Employee')

    def test_filter_by_gender(self):
        create_employee(name='Female Emp', email='female@example.com', gender='Female')
        response = self.client.get(reverse('employee_list'), {'gender': 'Female'})
        self.assertContains(response, 'Female Emp')
        self.assertNotContains(response, 'Test Employee')

    def test_search_no_results(self):
        response = self.client.get(reverse('employee_list'), {'search': 'zzznomatch'})
        self.assertContains(response, '0')

    def test_add_employee_get(self):
        response = self.client.get(reverse('add_employee'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/add_employee.html')

    def test_add_employee_valid_post(self):
        data = make_employee_data(email='new@example.com')
        response = self.client.post(reverse('add_employee'), data)
        self.assertRedirects(response, reverse('employee_list'))
        self.assertTrue(Employee.objects.filter(email='new@example.com').exists())

    def test_add_employee_auto_id_assigned(self):
        data = make_employee_data(email='new2@example.com')
        self.client.post(reverse('add_employee'), data)
        emp = Employee.objects.get(email='new2@example.com')
        self.assertTrue(emp.employee_id.startswith('EMP'))

    def test_add_employee_missing_name(self):
        data = make_employee_data(name='', email='noname@example.com')
        response = self.client.post(reverse('add_employee'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employee.objects.filter(email='noname@example.com').exists())

    def test_add_employee_duplicate_email(self):
        data = make_employee_data(email=self.emp.email)
        response = self.client.post(reverse('add_employee'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Employee.objects.filter(email=self.emp.email).count(), 1)

    def test_add_employee_negative_salary(self):
        data = make_employee_data(email='neg@example.com', salary=-500)
        response = self.client.post(reverse('add_employee'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employee.objects.filter(email='neg@example.com').exists())

    def test_add_employee_future_date(self):
        data = make_employee_data(email='future@example.com', date_of_joining='2099-01-01')
        response = self.client.post(reverse('add_employee'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employee.objects.filter(email='future@example.com').exists())

    def test_edit_employee_get(self):
        response = self.client.get(reverse('edit_employee', args=[self.emp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/edit_employee.html')

    def test_edit_employee_valid_post(self):
        data = make_employee_data(email=self.emp.email, name='Updated Name')
        response = self.client.post(reverse('edit_employee', args=[self.emp.id]), data)
        self.assertRedirects(response, reverse('employee_list'))
        self.emp.refresh_from_db()
        self.assertEqual(self.emp.name, 'Updated Name')

    def test_edit_employee_invalid_email(self):
        data = make_employee_data(email='bademail')
        response = self.client.post(reverse('edit_employee', args=[self.emp.id]), data)
        self.assertEqual(response.status_code, 200)

    def test_edit_nonexistent_employee_returns_404(self):
        response = self.client.get(reverse('edit_employee', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_employee_get_shows_confirmation(self):
        response = self.client.get(reverse('delete_employee', args=[self.emp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/delete_employee.html')

    def test_delete_employee_post_removes_record(self):
        emp_id = self.emp.id
        response = self.client.post(reverse('delete_employee', args=[emp_id]))
        self.assertRedirects(response, reverse('employee_list'))
        self.assertFalse(Employee.objects.filter(id=emp_id).exists())

    def test_delete_nonexistent_employee_returns_404(self):
        response = self.client.post(reverse('delete_employee', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_get_request_does_not_delete(self):
        """GET on delete page should NOT delete — only POST should."""
        self.client.get(reverse('delete_employee', args=[self.emp.id]))
        self.assertTrue(Employee.objects.filter(id=self.emp.id).exists())

    def test_employee_profile_loads(self):
        response = self.client.get(reverse('employee_profile', args=[self.emp.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_profile.html')

    def test_employee_profile_shows_correct_data(self):
        response = self.client.get(reverse('employee_profile', args=[self.emp.id]))
        self.assertContains(response, self.emp.name)
        self.assertContains(response, self.emp.employee_id)

    def test_profile_nonexistent_returns_404(self):
        response = self.client.get(reverse('employee_profile', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_export_csv_returns_file(self):
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('employees.csv', response['Content-Disposition'])

    def test_export_csv_contains_employee_data(self):
        response = self.client.get(reverse('export_csv'))
        content = response.content.decode('utf-8')
        self.assertIn(self.emp.name, content)
        self.assertIn(self.emp.email, content)
        self.assertIn(self.emp.employee_id, content)

    def test_export_csv_has_header_row(self):
        response = self.client.get(reverse('export_csv'))
        content = response.content.decode('utf-8')
        self.assertIn('Employee ID', content)
        self.assertIn('Name', content)
        self.assertIn('Email', content)

    def test_export_csv_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 302)


class AccountsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin123'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_wrong_password_shows_error(self):
        response = self.client.post(reverse('login'), {'username': 'admin', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')

    def test_wrong_username_shows_error(self):
        response = self.client.post(reverse('login'), {'username': 'nobody', 'password': 'admin123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')

    def test_empty_login_shows_error(self):
        response = self.client.post(reverse('login'), {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_to_login(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_home_redirects_to_dashboard_when_logged_in(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_home_redirects_to_login_when_logged_out(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
