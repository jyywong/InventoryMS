from rest_framework import serializers
from inventory.models import Lab, Inventory, Item, Item_Change_Log, Item_order
from django.contrib.auth.models import User

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'members']
        
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'lab', 'name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'inventory', 'name', 'e_date', 
                    'manufacturer', 'notes', 'bar_code', 'location_text', 'quantity']
                    
class ItemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item_Change_Log
        fields = ['action', 'item', 'user', 'quantity', 'date']

class ItemOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item_order
        fields = ['status', 'item', 'user', 'quantity', 'needed_by', 'notes']