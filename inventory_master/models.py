from django.db import models


class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.IntegerField()
    location = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.item_name