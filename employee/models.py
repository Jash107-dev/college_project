from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    salary = models.IntegerField()

    def __str__(self):
        return self.name