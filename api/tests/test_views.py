from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from inventory.models import Inventory, Item, Item_Change_Log, Item_order, Lab
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from datetime import date
from ..serializers import (InventorySerializer, ItemLogSerializer,
                          ItemOrderSerializer, ItemSerializer, LabSerializer)

# Create your tests here.
class APIUserAndLabSetUpTestCase(APITestCase):
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

class APILabListTests(APIUserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        # self.client.force_login(self.user)
        self.lab.members.add(self.user)
        self.url = reverse('api_lab_list')
        self.response = self.client.get(self.url)
    def test_api_lab_list_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_lab_list_logged_in(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_lab_list_has_correct_data(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data[0]['name'], 'Test Lab')
    def test_api_lab_list_successful_create_status_code(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
            "name": "New Test Lab",
            "members": [1]
        })
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    def test_api_lab_list_successful_lab_created(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
            "name": "New Test Lab",
            "members": [1]
        })
        self.assertEqual(Lab.objects.count(), 2)

class APIInventoryListTests(APIUserAndLabSetUpTestCase):
    def setUp(self):
        super().setUp()
        self.inv = Inventory.objects.create(
            lab = self.lab,
            name = 'Test Inv'
        )
        self.url = reverse('api_inv_list', kwargs={'lab_pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_api_inv_list_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_inv_list_logged_in_no_permission(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
    def test_api_inv_list_logged_in_has_permission(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_inv_list_has_correct_data(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data[0]['name'], 'Test Inv')
    def test_api_inv_list_successful_create_status_code(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
                "name": "New Test Inv",
        },)
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    def test_api_inv_list_successful_lab_created(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
            "name": "New Test Inv",
        },)
        self.assertEqual(Inventory.objects.count(), 2)

class APIItemListTests(APIUserAndLabSetUpTestCase):
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
        self.url = reverse('api_item_list', kwargs={'inv_pk': self.inv.id})
        self.response = self.client.get(self.url)
    def test_api_item_list_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_item_list_logged_in_no_permission(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
    def test_api_item_list_logged_in_has_permission(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_item_list_has_correct_data(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data[0]['name'], 'testitem')
    def test_api_item_list_successful_create_status_code(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
                "name": "New Test Inv",
                "manufacturer" : "testman",
                "e_date" : date.today(),
                "quantity" : 5
        },)
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    def test_api_item_list_successful_lab_created(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.post(self.url, {
                "name": "New Test Inv",
                "manufacturer" : "testman",
                "e_date" : date.today(),
                "quantity" : 5
        },)
        self.assertEqual(Item.objects.count(), 2)
class APIItemDetailTests(APIUserAndLabSetUpTestCase):
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
        self.url = reverse('api_item_detail', kwargs={'pk': self.item.id})
        self.response = self.client.get(self.url)
    def test_api_item_detail_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_item_detail_logged_in_no_permission(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
    def test_api_item_detail_logged_in_has_permission(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_item_detail_has_correct_data(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data['name'], 'testitem')
    def test_api_item_detail_can_patch_succesfully(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.patch(self.url, {
            "quantity" : 3
        })
        self.assertEqual(self.response.data['quantity'], 3)
    def test_api_item_detail_succesful_patch_creates_item_log(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.patch(self.url, {
            "quantity" : 3
        })
        self.assertEqual(Item_Change_Log.objects.count(), 1)
    def test_api_item_detail_succesful_patch_creates_correct_item_log(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.patch(self.url, {
            "quantity" : 3
        })
        self.assertEqual(Item_Change_Log.objects.first().quantity, 2)
    def test_api_item_detail_can_delete_succesfully(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.delete(self.url)
        self.assertEqual(Item.objects.count(), 0)

class APIItemLogListTests(APIUserAndLabSetUpTestCase):
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
        self.itemlog = Item_Change_Log.objects.create(
            action = 'Add',
            item = self.item,
            user = self.user,
            quantity = 2
        )
        self.url = reverse('api_item_change_log', kwargs={'item_pk': self.item.id})
        self.response = self.client.get(self.url)
    def test_api_item_log_list_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_item_log_list_logged_in_no_permission(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
    def test_api_item_log_list_logged_in_has_permission(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_item_log_list_has_correct_data(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data[0]['quantity'], 2)

class APIItemOrderTests(APIUserAndLabSetUpTestCase):
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
        self.order = Item_order.objects.create(
            item = self.item,
            status = 'Pending',
            user = self.user, 
            quantity = 3,
            needed_by = date.today(),
            notes = 'hello'
        )
        self.url = reverse('api_item_order', kwargs={'lab_pk': self.lab.id})
        self.response = self.client.get(self.url)
    def test_api_item_order_login_required(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_api_item_order_logged_in_no_permission(self):
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
    def test_api_item_order_logged_in_has_permission(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
    def test_api_item_log_list_has_correct_data(self):
        self.lab.members.add(self.user)
        self.client.force_authenticate(self.user)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.data[0]['quantity'], 3)
