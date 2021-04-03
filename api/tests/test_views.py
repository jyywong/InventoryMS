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