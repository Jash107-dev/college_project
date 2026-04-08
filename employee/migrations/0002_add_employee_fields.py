from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='employee_id',
            field=models.CharField(blank=True, max_length=20, unique=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=10),
        ),
        migrations.AddField(
            model_name='employee',
            name='designation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='date_of_joining',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('On Leave', 'On Leave')], default='Active', max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(blank=True, choices=[('HR', 'HR'), ('IT', 'IT'), ('Finance', 'Finance'), ('Marketing', 'Marketing'), ('Operations', 'Operations'), ('Sales', 'Sales'), ('Legal', 'Legal'), ('Admin', 'Admin')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(unique=True, max_length=254),
        ),
    ]