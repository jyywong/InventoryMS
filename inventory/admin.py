from django.contrib import admin
from inventory.models import Lab, Inventory, Item, Item_Change_Log, Item_order, LabInvite
# Register your models here.
admin.site.register(Lab)
admin.site.register(Inventory)
admin.site.register(Item)
admin.site.register(Item_Change_Log)
admin.site.register(Item_order)
admin.site.register(LabInvite)