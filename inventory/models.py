
from django.db import models
from core import settings

# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

class Inventory(models.Model):
    lab = models.ForeignKey(Lab, on_delete= models.CASCADE, related_name='lab')
    name = models.CharField(max_length=255)

class Item(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='inventory')
    name = models.CharField(max_length=255)
    e_date = models.DateField()
    manufacturer = models.CharField(max_length=255)
    notes = models.TextField()
    bar_code = models.BigIntegerField()
    location_text = models.TextField()
    quantity = models.IntegerField()

class Item_Change_Log(models.Model):
    action_choices = [
        ('Add', 'Add'),
        ('Remove', 'Remove'),
    ]
    action = models.CharField(
        max_length=100,
        choices=action_choices,
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now= True)

class Item_order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_item')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_user')
    quantity = models.IntegerField()
    needed_by = models.DateField()
    notes = models.TextField(default='')