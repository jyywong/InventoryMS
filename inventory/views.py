from django.shortcuts import render, redirect
from .models import Lab, Inventory, Item, Item_Change_Log, Item_order, LabInvite
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, DetailView, DeleteView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django import forms
from .forms import InviteForm
from core import settings
from django.core.exceptions import PermissionDenied
from json import dumps
# Create your views here.



class Home(LoginRequiredMixin, TemplateView):
    template_name = 'homepage.html'

'''
Permission mixins 
'''
class LabMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        lab = Lab.objects.get(id = self.kwargs['pk'])
        return user in lab.members.all()

class InventoryMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        inv = Inventory.objects.get(id = self.kwargs['pk'])
        return user in inv.lab.members.all()

class ItemMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        item = Item.objects.get(id = self.kwargs['pk'])
        return user in item.inventory.lab.members.all()

'''
Lab related views
'''

class Lab_Create(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Lab
    fields = ['name'] 
    template_name = 'create_lab.html'

    def get_success_url(self):
        return reverse('lab_list')
    
    def form_valid(self, form):
        object = form.save()
        object.members.add(self.request.user)
        object.save()
        return super(Lab_Create, self).form_valid(form)

class LabList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Lab
    context_object_name = 'labs'
    template_name='my_labs.html'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Lab.objects.filter(members= user)
        return queryset

class LabView(LabMixin, DetailView):
    login_url = 'login'
    model = Lab
    context_object_name = "lab"

    template_name = "lab_detail.html"

    def get_context_data(self, *args, **kwargs):
        this_lab = Lab.objects.get(id = self.kwargs['pk'])
        inv_traffic_JSON = dumps(this_lab.get_traffic_per_inventory())
        context = super().get_context_data(**kwargs)
        context['members'] = this_lab.members.all()
        context['invs'] = Inventory.objects.filter(lab = this_lab)
        context['inv_count'] = Inventory.objects.filter(lab = this_lab).count()
        context['item_count'] = Item.objects.filter(inventory__lab = this_lab).count()
        context['item_per_lab'] = Item.objects.filter()
        context['inv_traffic'] = inv_traffic_JSON
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory__lab = this_lab) & 
                Q(status = "Pending")
            ).count()
        return context

class LabAdd(LabMixin, UpdateView):
    login_url = 'login'
    model = Lab
    fields = ['members']
    context_object_name = "lab"
    template_name ="lab_member_add.html"

    def get_success_url(self):
            return reverse('lab_view', args =(self.object.id,))

class InviteMember(LabMixin, FormView):
    login_url = 'login'
    template_name = 'invite_member.html'
    form_class = InviteForm
    success_url = reverse_lazy('homepage')
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab'] = Lab.objects.get(id = self.kwargs['pk'])
        return context
    def form_valid(self, form):
        LabInvite.objects.create(
            invitee = get_user_model().objects.get(email = form.cleaned_data['user_email']),
            lab_inviter = Lab.objects.get(id = self.kwargs['pk']),
            status = 'Pending'
        )
        return super(InviteMember, self).form_valid(form)

@login_required
def RemoveMember(request, lab_pk, user_pk):
    lab = Lab.objects.get(id = lab_pk)
    user = get_user_model().objects.get(id = user_pk)
    if request.user not in lab.members.all():
        raise PermissionDenied()
    else: 
        context = {
            'user' : user,
            'lab' : lab
        }

        if request.method == "POST":
            if request.POST.get('Confirm'):
                lab.remove_member(user)
                lab.save()
                return redirect('lab_view', pk = lab.id)
        return render(request, 'remove_member.html', context)

class LabOrderList(LabMixin, ListView):
    login_url = 'login'
    model = Item_order
    context_object_name = 'orders'
    template_name='lab_order_list.html'

    def get_queryset(self):
        queryset = Item_order.objects.filter(
            item__inventory__lab = Lab.objects.get(id = self.kwargs['pk'])
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        this_lab = Lab.objects.get(id = self.kwargs['pk'])
        context['lab'] = this_lab
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory__lab = this_lab) & 
                Q(status = "Pending")
            ).count()
        return context

'''
Inventory related views
'''

class Inventory_Create(LabMixin, CreateView):
    login_url = 'login'
    model = Inventory
    fields = ['name']
    template_name = 'create_inv.html'
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab'] = Lab.objects.get(id = self.kwargs['pk'])
        return context

    def form_valid(self, form):
        object = form.save(commit = False)
        object.lab = Lab.objects.get(id = self.kwargs['pk'])
        object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('lab_view', args =(self.kwargs['pk'],))

class InvList(LabMixin, ListView):
    login_url = 'login'
    model = Inventory
    context_object_name = 'invs'
    template_name='lab_invs.html'

    def get_queryset(self):
        queryset = Inventory.objects.filter(lab = self.kwargs['pk'])
        return queryset
    

class InventoryDelete(InventoryMixin, DeleteView):
    login_url = 'login'
    model = Inventory
    template_name = 'delete_inventory.html'

    def get_success_url(self):
        inv = Inventory.objects.get(id = self.kwargs['pk'])
        lab = inv.lab
        return reverse('lab_view',args =(lab.id,) )

    def get_context_data(self, *args, **kwargs):
        this_inv = Inventory.objects.get(id = self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(inventory = this_inv)
        context['item_count'] = Item.objects.filter(inventory = this_inv).count()
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory = this_inv) & 
                Q(status = "Pending")
            ).count()
        return context

class Inventory_Update(LabMixin, UpdateView):
    login_url = 'login'
    model = Inventory
    fields = ['item']
    template_name = 'create_lab.html'

    
class InvView(InventoryMixin, DetailView):
    login_url = 'login'
    model = Inventory
    context_object_name = "inv"

    template_name = "inv_detail.html"

    def get_context_data(self, *args, **kwargs):
        this_inv = Inventory.objects.get(id = self.kwargs['pk'])
        
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(inventory = this_inv)
        context['item_count'] = Item.objects.filter(inventory = this_inv).count()
        context['item_traffic'] = this_inv.get_traffic_per_item()
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory = this_inv) & 
                Q(status = "Pending")
            ).count()
        return context

class InventoryOrderList(InventoryMixin, ListView):
    login_url = 'login'
    model = Item_order
    context_object_name = 'orders'
    template_name = 'inv_order_list.html'

    def get_queryset(self):
        queryset = Item_order.objects.filter(
            item__inventory = Inventory.objects.get(id = self.kwargs['pk'])
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        this_inv = Inventory.objects.get(id = self.kwargs['pk'])
        context['inv'] = this_inv
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory = this_inv) & 
                Q(status = "Pending")
            ).count()
        return context

'''
Item related views
'''
    
class Item_Create(InventoryMixin, CreateView):
    login_url = 'login'
    model = Item
    fields = ['name', 'e_date', 'manufacturer', 'notes', 'quantity']
    template_name = 'create_item.html'
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        this_inv = Inventory.objects.get(id = self.kwargs['pk'])
        context['inventory'] = this_inv
        context['lab'] = this_inv.lab
        return context

    def get_form(self, form_class = None):
        form = super(Item_Create, self).get_form(form_class)
        form.fields['e_date'].widget = forms.DateTimeInput(attrs={'type':'date'})
        return form
    def form_valid(self, form):
        object = form.save(commit = False)
        object.inventory = Inventory.objects.get(id = self.kwargs['pk'])
        object.save()

        return super().form_valid(form)
    def get_success_url(self):
        return reverse('inventory_view',args =(self.kwargs['pk'],) )

class Item_Delete(ItemMixin, DeleteView):
    login_url = 'login'
    model = Item
    template_name = 'delete_item.html'

    def get_success_url(self):
        item = Item.objects.get(id = self.kwargs['pk'])
        inv = item.inventory
        return reverse('inventory_view',args =(inv.id,) )

class ItemList(InventoryMixin, ListView):
    login_url = 'login'
    model = Item
    context_object_name = 'items'
    template_name='item_list.html'

    def get_queryset(self):
        queryset = Item.objects.filter(inventory = self.kwargs['pk'])
        return queryset
 
class ItemView(ItemMixin, DetailView):
    login_url = 'login'
    model = Item
    context_object_name = "item"

    template_name = "item_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logs'] = Item_Change_Log.objects.filter(item = Item.objects.get(id = self.kwargs['pk'])).order_by('-date')
        context['percent'] = Item_Change_Log.percent_of_last_restock(Item.objects.get(id = self.kwargs['pk']) )
        return context

class ItemAdd(ItemMixin, UpdateView):
    login_url = 'login'
    model = Item
    fields = ['quantity']
    context_object_name = "item"
    template_name ="item_add.html"
    def form_valid(self, form):
        object = form.save(commit = False)
        change = object.quantity
        object.quantity += Item.objects.get(id = self.kwargs['pk']).quantity 
        object.save()
        Item_Change_Log.objects.create(
            item = Item.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            quantity = change,
            action = 'Add'
        )
        return super().form_valid(form)
    def get_success_url(self):
            return reverse('item_view', args =(self.object.id,))

class ItemRemove(ItemMixin, UpdateView):
    login_url = 'login'
    model = Item
    fields = ['quantity']
    context_object_name = "item"
    template_name ="item_remove.html"


    def form_valid(self, form):
        object = form.save(commit = False)
        change = object.quantity
        object.quantity = Item.objects.get(id = self.kwargs['pk']).quantity - object.quantity
        object.save()
        Item_Change_Log.objects.create(
            item = Item.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            quantity = change,
            action = 'Remove'
        )
        return super().form_valid(form)
    def get_success_url(self):
            return reverse('item_view', args =(self.object.id,))

class ItemOrderCreate(ItemMixin, CreateView):
    login_url = 'login'
    model = Item_order
    fields = ['quantity', 'needed_by', 'notes']
    template_name = 'create_order.html'

    def get_form(self, form_class = None):
        form = super(ItemOrderCreate, self).get_form(form_class)
        form.fields['needed_by'].widget = forms.DateTimeInput(attrs={'type':'date'})
        return form
    def form_valid(self,form):
        object = form.save(commit=False)
        object.item = Item.objects.get(id = self.kwargs['pk'])
        object.user = self.request.user
        object.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = Item.objects.get(id = self.kwargs['pk'])
        
        return context

    def get_success_url(self):
        return reverse('home')


'''
Other views
'''

class OrderList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Item_order
    context_object_name = 'orders'
    template_name='order_list2.html'

    def get_queryset(self):
        user = self.request.user
 

        queryset = Item_order.objects.filter(
            item__inventory__lab__members = user
        ).order_by('-created_at')
        return queryset

@login_required
def OrderDetail(request, pk):
    order = Item_order.objects.get(id=pk)
    lab = order.item.inventory.lab
    if request.user not in lab.members.all():
        raise PermissionDenied()
    else: 
        context = {
            'order' : order,
        }

        if request.method == "POST":
            if request.POST.get('Approve'):
                order.status = 'Approved'
                order.save()

            elif request.POST.get('Reject'):
                order.status = 'Rejected'
                order.save()
        return render(request, 'order_detail.html', context)

    
class InviteList(ListView):
    login_url = 'login'
    template_name = 'invite_list.html' 
    model = LabInvite 
    context_object_name = 'invites'

    def get_queryset(self):
        user = self.request.user
        queryset = LabInvite.objects.filter(invitee = user).order_by('created_at')
        return queryset

@login_required
def InviteDetail(request, pk):
    invite = LabInvite.objects.get(id = pk)
    if request.user != invite.invitee:
        raise PermissionDenied()
    
    else: 
        context = {
        'invite' : invite,
        }
        if request.method == "POST":
            print('hello')
            if request.POST.get('Accept'):
                invite.status = 'Accepted'
                invite.AcceptInvite()
                invite.save()
        return render(request, 'invite_detail.html', context)


