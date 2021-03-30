from inventory.models import Lab, Inventory, Item, Item_Change_Log, Item_order


from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import LabSerializer, InventorySerializer, ItemSerializer, ItemLogSerializer, ItemOrderSerializer
from rest_framework import generics
from rest_framework import permissions
from api.permissions import IsMemberOfLab
# Create your views here.



class LabList(generics.ListCreateAPIView):
    serializer_class = LabSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Lab.objects.filter(members = user)
    

class InventoryList(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsMemberOfLab]

    def get_queryset(self):
        lab_pk = self.kwargs['lab_pk']
        return Inventory.objects.filter(lab = lab_pk)


class ItemList(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    permission_classes = [IsMemberOfLab]
    serializer_class = ItemSerializer

    def get_queryset(self):
        inv_pk = self.kwargs['inv_pk']
        return Item.objects.filter(inventory = inv_pk)

class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsMemberOfLab]

    def patch(self, request, *args, **kwargs):
        current_quantity = self.get_object().quantity
        new_quantity = int(request.data['quantity'])
        if current_quantity > new_quantity:
            action = 'Remove'
            change = current_quantity - new_quantity
        elif current_quantity < new_quantity:
            action = 'Add'
            change = new_quantity - current_quantity
        Item_Change_Log.objects.create(
            item = self.get_object(),
            user = self.request.user,
            quantity = change,
            action = action
        )
        return super().patch(request, *args, **kwargs)

class ItemLogList(generics.ListAPIView):
    serializer_class = ItemLogSerializer
    permission_classes = [IsMemberOfLab]
    def get_queryset(self):
        item_pk = self.kwargs['item_pk']
        return Item_Change_Log.objects.filter(item = item_pk).order_by('-date')

class ItemOrder(generics.ListAPIView):
    serializer_class = ItemOrderSerializer
    permission_classes = [IsMemberOfLab]
    def get_queryset(self):
        lab_pk = self.kwargs['lab_pk']
        return Item_order.objects.filter(item__inventory__lab = lab_pk)
