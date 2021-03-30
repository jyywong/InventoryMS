from rest_framework import permissions
from inventory.models import Lab, Inventory, Item

class IsMemberOfLab(permissions.BasePermission):
    message = 'You do not have permission to view this.'

    def has_permission(self, request, view):
        user = request.user
        if 'lab_pk' in view.kwargs:
            lab_pk = view.kwargs['lab_pk']
            lab = Lab.objects.get(id = lab_pk)
            return user in lab.members.all()
        elif 'inv_pk' in view.kwargs:
            inv_pk = view.kwargs['inv_pk']
            inv = Inventory.objects.get(id = inv_pk)
            return user in inv.lab.members.all()
        elif 'item_pk' in view.kwargs:
            item_pk = view.kwargs['item_pk']
            item = Item.objects.get(id = item_pk)
            return user in item.inventory.lab.members.all()
        elif 'pk' in view.kwargs:
            item_pk = view.kwargs['pk']
            item = Item.objects.get(id = item_pk)
            return user in item.inventory.lab.members.all()



