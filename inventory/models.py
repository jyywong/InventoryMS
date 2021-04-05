
from django.db import models
from core import settings
from django.db.models import Q
from datetime import date, datetime
import datetime as dt
# Create your models here.
class Lab(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name
    def remove_member(self, member):
        self.members.remove(member)
    def get_traffic_per_inventory(self):
        inv_traffic = dict((inv.name, 0) for inv in self.inventory.all())
        for inv in self.inventory.all():
            inv_traffic[inv.name] += inv.get_all_traffic()
        return inv_traffic


class Inventory(models.Model):
    lab = models.ForeignKey(Lab, on_delete= models.CASCADE, related_name='inventory', blank = True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    def get_all_traffic(self):
        total_traffic = 0
        for item in self.item.all():
            total_traffic += Item_Change_Log.item_traffic_last_month(item)
        return total_traffic
    def get_traffic_per_item(self):
        item_traffic = dict((item.name, 0) for item in self.item.all())
        for item in self.item.all():
            item_traffic[item.name] += Item_Change_Log.item_traffic_last_month(item)
        return item_traffic

class Item(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='item', blank = True)
    name = models.CharField(max_length=255)
    e_date = models.DateField(blank =True, null=True)
    manufacturer = models.CharField(max_length=255, blank = True)
    notes = models.TextField(blank=True)
    bar_code = models.BigIntegerField(blank =True, null=True)
    location_text = models.TextField(blank =True)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name

        

class Item_Change_Log(models.Model):
    action_choices = [
        ('Add', 'Add'),
        ('Remove', 'Remove'),
    ]
    action = models.CharField(
        max_length=100,
        choices=action_choices,
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_change_log')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    quantity_changed = models.IntegerField()
    date = models.DateTimeField(auto_now= True)
    new_quantity = models.IntegerField(blank=True, null=True)

    @staticmethod
    def get_most_recent_restock(item):
        item_change_log = Item_Change_Log.objects.filter(item = item).order_by('-date')
        for log in item_change_log:
            if log.action == 'Add':
                return log.quantity_changed
    @staticmethod
    def percent_of_last_restock(item):
        if Item_Change_Log.get_most_recent_restock(item):
            return (item.quantity / Item_Change_Log.get_most_recent_restock(item))* 100
        else: 
            return 0

    @staticmethod
    def item_traffic_last_month(item):
        past_month_change_logs = Item_Change_Log.objects.filter(
            Q(item = item) &
            Q(date__range =  (datetime.now() - dt.timedelta(days = 30), datetime.now())) &
            Q(action = 'Remove')
        )
        print(datetime.now() - dt.timedelta(days = 30))
        print(past_month_change_logs)
        total = 0
        for logs in past_month_change_logs:
            total += logs.quantity_changed
        return total 
    @staticmethod
    def quantity_over_past_30_days(item):
        thirty_days_ago = date.today() - dt.timedelta(days = 30)
        days =[]
        for i in range(31):
            days.append(thirty_days_ago + dt.timedelta(days = i))
        total = dict((datetime.strftime(day,"%Y-%m-%d"), 0) for day in days)
        for key in total:
            this_date = datetime.strptime(key, "%Y-%m-%d")
            if Item_Change_Log.objects.filter(item = item).filter(date__range = (this_date, this_date + dt.timedelta(hours=24))).count() > 0 :
                print('hello')
                total[key] = Item_Change_Log.objects.filter(
                    Q(date__range = (this_date, this_date + dt.timedelta(hours=24))) &
                    Q(item = item)
                    ).order_by('-date').first().new_quantity
        return total
            



class Item_order(models.Model):
    status_choices = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=100,
        choices=status_choices,
        default = 'Pending'
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_order')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='item_order')
    quantity = models.IntegerField()
    needed_by = models.DateField()
    created_at = models.DateField(auto_now=True )
    notes = models.TextField(default='')
    
class LabInvite(models.Model):
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name='lab_invite')
    lab_inviter = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='lab_invite')
    created_at = models.DateField(auto_now= True)
    status_choices = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
    ]
    status = models.CharField(
        max_length=100,
        choices=status_choices,
        default = 'Pending'
    )

    def AcceptInvite(self):
        self.lab_inviter.members.add(self.invitee)
