from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    course = models.CharField(max_length=100)
    year = models.IntegerField()
    date_of_birth = models.DateField()
    address = models.TextField()
    

    def __str__(self):
        return self.name
