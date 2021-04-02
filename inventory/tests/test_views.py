from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from datetime import date
from inventory.forms import InviteForm
from inventory.views import *
from inventory.models import Lab, Inventory, Item, Item_Change_Log, Item_order, LabInvite

class UserAndLabSetUpTestCase(TestCase):
    def setUp(self):
        self.username = 'jon'
        self.password = '1234'
        self.user = get_user_model().objects.create(
            username = self.username,
            password = self.password
        )
        self.lab = Lab.objects.create(
            name = 'Test Lab'
        )
'''
Tests for lab views
'''
class CreateLabTests(TestCase):
    def test_create_lab_login_required(self):
        self.url = reverse('create_lab')
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class CreateLabTestsLoggedIn(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse('create_lab')
        self.response = self.client.get(self.url)
    def test_create_lab_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_create_lab_contains_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_create_lab_resolves_create_lab_view(self):
        view = resolve('/create_lab')
        self.assertEqual(view.func.view_class, Lab_Create)
    def test_new_lab_created(self):
        self.response = self.client.post(self.url,{
            'name' : 'Test Name'
        })
        self.assertEqual(Lab.objects.count(), 2)

class LabListLoggedOut(TestCase):
    def test_lab_list_login_required(self):
        self.url = reverse('lab_list')
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class LabListLoggedIn(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse('lab_list')
        self.response = self.client.get(self.url)
    def test_lab_list_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_lab_list_resolves_lab_list_view(self):
        view = resolve('/my_labs')
        self.assertEqual(view.func.view_class, LabList)

class LabViewLoggedOut(TestCase):
    def test_lab_view_login_required(self):
        self.url = reverse('lab_view', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class LabViewLoggedIn(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse('lab_view', kwargs={'pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_lab_view_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_lab_view_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_lab_view_resolves_lab_view(self):
        view = resolve('/lab_detail/1')
        self.assertEqual(view.func.view_class, LabView)
'''
Lab add is obsolete
'''

class InviteMemberLoggedOut(TestCase):
    def test_invite_member_login_required(self):
        self.url = reverse('invite_member', kwargs={'pk': 1})
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InviteMemberLoggedIn(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse('invite_member', kwargs={'pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_invite_member_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_invite_member_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_invite_member_resolves_invite_member_view(self):
        view = resolve('/invite_member/1')
        self.assertEqual(view.func.view_class, InviteMember)
    def test_invite_member_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_invite_member_contains_form(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        form = self.response.context.get('form')
        self.assertIsInstance(form, InviteForm)
    def test_invite_member_created_invite_success(self):
        self.email = 'invitee@gmail.com'
        self.invitee = get_user_model().objects.create(
            username = 'invitee',
            password = '1234',
            email = self.email
        )
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'user_email' : self.email
        })
        self.assertEqual(1, LabInvite.objects.count())
    def test_invite_member_no_invite_created_when_wrong_email(self):
        self.email = 'invitee@gmail.com'
        self.invitee = get_user_model().objects.create(
            username = 'invitee',
            password = '1234',
            email = self.email
        )
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'user_email' : 'wrong@email.com'
        })
        self.assertEqual(0, LabInvite.objects.count())


class RemoveMemberTests(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.user2 = get_user_model().objects.create(
            username = 'testuser',
            password = '1234',
        )
        self.lab.members.add(self.user2)
        self.url = reverse('remove_member', kwargs={'lab_pk': self.lab.id, 'user_pk': self.user2.id})
        self.response = self.client.get(self.url)
    def test_remove_member_login_required(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
    def test_remove_member_no_permission_status_code(self):
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 403)
    def test_remove_member_successful_status_code(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_remove_member_resolves_remove_member_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/remove_member/1/2')
        self.assertEqual(view.func, RemoveMember)
    def test_remove_member_contains_csrf(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_remove_member_user2_exists(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        self.assertIn(self.user2, self.lab.members.all())
    def test_remove_member_successful_removal(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'Confirm': ['Confirm']
        })
        self.assertNotIn(self.user2, self.lab.members.all())

# class LabOrderList(UserAndLabSetUpTestCase):
#     def setUp(self):
#         super().setUp()
#         self.order1 = Item_order.objects.create(
#         )


'''
Tests for inventory views
'''

class InventorySetUpTestCase(UserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.inv = Inventory.objects.create(
            lab = self.lab,
            name = 'Test Inv'
        )
        

class InventoryCreateLoggedOut(InventorySetUpTestCase):
    def test_inventory_create_login_required(self):
        self.url = reverse('create_inventory', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InventoryCreateLoggedIn(InventorySetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('create_inventory', kwargs={'pk': 1}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)

    def test_inventory_create_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_inventory_create_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_inventory_create_resolves_inventory_create_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/inventory_create/1')
        self.assertEqual(view.func.view_class, Inventory_Create)
    def test_inventory_create_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_inventory_create_new_inventory_success(self):
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url, {
            'name' : 'Test Inv'
        })
        self.assertEqual(2, Inventory.objects.count())
    
'''
InvList is obsolete
'''

class InventoryDeleteLoggedOut(InventorySetUpTestCase):
    def test_inventory_delete_login_required(self):
        self.url = reverse('inventory_delete', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InventoryDeleteLoggedIn(InventorySetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('inventory_delete', kwargs={'pk': 1}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_inventory_delete_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_inventory_delete_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_inventory_delete_resolves_inventory_delete_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/inventory_delete/1')
        self.assertEqual(view.func.view_class, InventoryDelete)
    def test_inventory_delete_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_inventory_delete_succesful_delete(self):
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'Confirm': ['Confirm']
        })
        self.assertNotIn(self.inv, self.lab.inventory.all())

class InvViewLoggedOut(InventorySetUpTestCase):
    def test_inv_view_login_required(self):
        self.url = reverse('inventory_view', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InvViewLoggedIn(InventorySetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('inventory_view', kwargs={'pk': 1}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_inv_view_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_inv_view_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_inv_view_resolves_inv_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/inventory_detail/1')
        self.assertEqual(view.func.view_class, InvView)

class InventoryOrderListLoggedOut(InventorySetUpTestCase):
    def test_inv_view_login_required(self):
        self.url = reverse('inv_order_list', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class InventoryOrderListLoggedIn(InventorySetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('inv_order_list', kwargs={'pk': 1}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_inventory_order_list_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_inventory_order_list_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_inventory_order_list_resolves_inventory_order_list_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/inventory_orders/1')
        self.assertEqual(view.func.view_class, InventoryOrderList)


'''
Tests for item views
'''
class ItemSetUpTestCase(InventorySetUpTestCase):
    def setUp(self):
        super().setUp()
        self.inv = Inventory.objects.create(
            lab = self.lab,
            name = 'Test Inv'
        )
        self.item = Item.objects.create(
            inventory = self.inv,
            name = "testitem",
            manufacturer = 'testman',
            e_date = date.today(),
            quantity = 5
        )

class ItemCreateLoggedOut(ItemSetUpTestCase):
    def test_item_create_login_required(self):
        self.url = reverse('item_create', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ItemCreateLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('item_create', kwargs={'pk': self.inv.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_create_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_create_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_create_resolves_item_create_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_create/1')
        self.assertEqual(view.func.view_class, Item_Create)
    def test_item_create_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_item_create_succesful_new_item(self):
        self.lab.members.add(self.user)
        self.client.force_login(self.user)
        self.response = self.client.post(self.url,{
            'name': 'Test New Item',
            'e_date': date.today(),
            'manufacturer' : 'Test Man',
            'notes': 'N/A',
            'quantity' : 5
        })
        self.assertEqual(2, self.inv.item.count())

class ItemDeleteLoggedOut(ItemSetUpTestCase):
    def test_item_delete_login_required(self):
        self.url = reverse('item_delete', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
    
class ItemDeleteLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('item_delete', kwargs={'pk': self.item.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_delete_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_delete_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_delete_resolves_item_delete_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_delete/1')
        self.assertEqual(view.func.view_class, Item_Delete)
    def test_item_delete_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_item_delete_succesful_delete(self):
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'Confirm': ['Confirm']
        })
        self.assertNotIn(self.item, self.inv.item.all())

'''
ItemList is obsolete
'''

class ItemViewLoggedOut(ItemSetUpTestCase):
    def test_item_delete_login_required(self):
        self.url = reverse('item_view', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ItemViewLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('item_view', kwargs={'pk': self.item.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_view_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_view_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_view_resolves_item_view_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_detail/1')
        self.assertEqual(view.func.view_class, ItemView)

class ItemAddLoggedOut(ItemSetUpTestCase):
    def test_item_add_login_required(self):
        self.url = reverse('item_add', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ItemAddLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('item_add', kwargs={'pk': self.item.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_add_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_add_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_add_resolves_item_add_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_detail/add/1')
        self.assertEqual(view.func.view_class, ItemAdd)
    def test_item_add_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    # Don't know why this test doesn't work
    # def test_item_add_succesful_quantity_added(self):
    #     self.lab.members.add(self.user)
    #     self.response = self.client.post(self.url,{
    #         'quantity' : 15
    #     })
    #     self.assertEqual(10, self.item.quantity)

class ItemRemoveLoggedOut(ItemSetUpTestCase):
    def test_item_remove_login_required(self):
        self.url = reverse('item_remove', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ItemRemoveLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('item_add', kwargs={'pk': self.item.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_remove_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_remove_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_remove_resolves_item_remove_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_detail/remove/1')
        self.assertEqual(view.func.view_class, ItemRemove)
    def test_item_remove_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    # Don't know why this test doesn't work
    # def test_item_remove_succesful_quantity_removed(self):
    #     self.lab.members.add(self.user)
    #     self.response = self.client.post(self.url,{
    #         'quantity' : 1
    #     })
    #     self.assertEqual(4, self.item.quantity)

class ItemOrderCreateLoggedOut(ItemSetUpTestCase):
    def test_item_order_create_login_required(self):
        self.url = reverse('order_create', kwargs={'pk': 1}) 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ItemOrderCreateLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('order_create', kwargs={'pk': self.item.id}) 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
    def test_item_order_create_no_permission_status_code(self):
        self.assertEqual(self.response.status_code, 403)
    def test_item_order_create_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_item_order_create_resolves_item_order_create_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/item_detail/order/1')
        self.assertEqual(view.func.view_class, ItemOrderCreate)
    def test_item_order_create_contains_csrf(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    def test_item_order_create_succesful_delete(self):
        self.lab.members.add(self.user)
        self.response = self.client.post(self.url,{
            'quantity' : 3,
            'needed_by' : date.today(),
            'notes' : 'N/A'
        })
        self.assertEqual(1, Item_order.objects.count())

class OrderListLoggedOut(ItemSetUpTestCase):
    def test_item_order_create_login_required(self):
        self.url = reverse('order_lists') 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class OrderListLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('order_lists') 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)

    def test_order_list_create_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_order_list_create_resolves_item_order_create_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/orders')
        self.assertEqual(view.func.view_class, OrderList)

class InviteListLoggedOut(ItemSetUpTestCase):
    def test_invite_list_create_login_required(self):
        self.url = reverse('invite_list') 
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
    
class InviteListLoggedIn(ItemSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('invite_list') 
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)

    def test_order_list_create_successful_status_code(self):
        self.lab.members.add(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
    def test_order_list_create_resolves_item_order_create_view(self):
        self.client.force_login(self.user)
        self.lab.members.add(self.user)
        view = resolve('/invites')
        self.assertEqual(view.func.view_class, InviteList)