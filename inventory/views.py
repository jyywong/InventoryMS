from django.shortcuts import render, redirect
from .models import Lab, Inventory, Item, Item_Change_Log, Item_order
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, DetailView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.db.models import Q
from django import forms

# Create your views here.



class Home(TemplateView):
    template_name = 'index.html'

class Lab_Create(CreateView):
    model = Lab
    fields = ['name', 'members'] 
    template_name = 'create_lab.html'
    def get_success_url(self):
        return reverse('create_inventory', args =(self.object.id,))

class LabView(DetailView):
    model = Lab
    context_object_name = "lab"

    template_name = "lab_detail.html"

    def get_context_data(self, *args, **kwargs):
        this_lab = Lab.objects.get(id = self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['members'] = this_lab.members.all()
        context['invs'] = Inventory.objects.filter(lab = this_lab)
        context['inv_count'] = Inventory.objects.filter(lab = this_lab).count()
        context['item_count'] = Item.objects.filter(inventory__lab = this_lab).count()
        context['item_per_lab'] = Item.objects.filter()
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory__lab = this_lab) & 
                Q(status = "Pending")
            ).count()
        return context

class LabAdd(UpdateView):
    model = Lab
    fields = ['members']
    context_object_name = "lab"
    template_name ="lab_member_add.html"

    def get_success_url(self):
            return reverse('lab_view', args =(self.object.id,))

class Inventory_Create(CreateView):
    model = Inventory
    fields = ['name']
    template_name = 'create_inv.html'
    def form_valid(self, form):
        object = form.save(commit = False)
        object.lab = Lab.objects.get(id = self.kwargs['pk'])
        object.save()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse('item_create')

class Inventory_Update(UpdateView):
    model = Inventory
    fields = ['item']
    template_name = 'create_lab.html'
    
class InvView(DetailView):
    model = Inventory
    context_object_name = "inv"

    template_name = "inv_detail.html"

    def get_context_data(self, *args, **kwargs):
        this_inv = Inventory.objects.get(id = self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(inventory = this_inv)
        context['item_count'] = Item.objects.filter(inventory = this_inv).count()
        context['order_count'] = Item_order.objects.filter(
                Q(item__inventory__lab = this_inv.lab) & 
                Q(status = "Pending")
            ).count()
        return context
    
    
class Item_Create(CreateView):
    model = Item
    fields = ['name', 'e_date', 'manufacturer', 'notes', 'quantity']
    template_name = 'create_item.html'
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

class Item_Delete(DeleteView):
    model = Item
    template_name = 'delete_item.html'

    def get_success_url(self):
        item = Item.objects.get(id = self.kwargs['pk'])
        inv = item.inventory
        return reverse('inventory_view',args =(inv.id,) )

class LabList(ListView):
    model = Lab
    context_object_name = 'labs'
    template_name='my_labs.html'
    

    def get_queryset(self):
        user = self.request.user
        queryset = Lab.objects.filter(members= user)
        return queryset

class InvList(ListView):
    model = Inventory
    context_object_name = 'invs'
    template_name='lab_invs.html'

    def get_queryset(self):
        queryset = Inventory.objects.filter(lab = self.kwargs['pk'])
        return queryset
    
class ItemList(ListView):
    model = Item
    context_object_name = 'items'
    template_name='item_list.html'

    def get_queryset(self):
        queryset = Item.objects.filter(inventory = self.kwargs['pk'])
        return queryset
 
    
class ItemView(DetailView):
    model = Item
    context_object_name = "item"

    template_name = "item_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logs'] = Item_Change_Log.objects.filter(item = Item.objects.get(id = self.kwargs['pk'])).order_by('-date')
        context['percent'] = Item_Change_Log.percent_of_last_restock(Item.objects.get(id = self.kwargs['pk']) )
        return context

class ItemAdd(UpdateView):
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

class ItemRemove(UpdateView):
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

class ItemOrderCreate(CreateView):
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

class LabOrderList(ListView):
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
        context['lab'] = Lab.objects.get(id = self.kwargs['pk'])
        return context

class OrderList(ListView):
    model = Item_order
    context_object_name = 'orders'
    template_name='order_list2.html'

    def get_queryset(self):
        user = self.request.user
 

        queryset = Item_order.objects.filter(
            item__inventory__lab__members = user
        )
        return queryset

def OrderDetail(request, pk):
    order = Item_order.objects.get(id=pk)
    context = {
        'order' : order,
    }

    if request.method == "POST":
        if request.POST.get('Approve'):
            print('hello')
            order.status = 'Approved'
            order.save()

        elif request.POST.get('Reject'):
            order.status = 'Reject'
            order.save()
    return render(request, 'order_detail.html', context)

    



